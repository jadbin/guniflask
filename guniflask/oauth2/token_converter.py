# coding=utf-8

from typing import Optional
from abc import ABCMeta, abstractmethod
import datetime as dt
import re

from guniflask.security.authentication import Authentication
from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.user_details_service import UserDetailsService
from guniflask.security.jwt import JwtHelper
from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.token import OAuth2AccessToken, OAuth2RefreshToken
from guniflask.oauth2.request import OAuth2Request
from guniflask.oauth2.errors import InvalidTokenError

__all__ = ['AccessTokenConverter', 'TokenEnhancer', 'UserAuthenticationConverter',
           'DefaultAccessTokenConverter', 'JwtAccessTokenConverter']


class AccessTokenConverter(metaclass=ABCMeta):
    """
    Converter interface for token service implementations that store authentication data inside the token.
    """

    AUD = 'aud'
    CLIENT_ID = 'client_id'
    EXP = 'exp'
    JTI = 'jti'
    ATI = 'ati'
    SCOPE = OAuth2AccessToken.SCOPE
    AUTHORITIES = 'authorities'

    @abstractmethod
    def convert_access_token(self, token: OAuth2AccessToken, authentication: OAuth2Authentication) -> dict:
        pass

    @abstractmethod
    def extract_access_token(self, token_value: str, data: dict) -> OAuth2AccessToken:
        pass

    @abstractmethod
    def extract_authentication(self, data: dict) -> OAuth2Authentication:
        pass


class DefaultAccessTokenConverter(AccessTokenConverter):
    def __init__(self):
        self.user_token_converter = UserAuthenticationConverter()

    def convert_access_token(self, token: OAuth2AccessToken, authentication: OAuth2Authentication) -> dict:
        result = {}
        client_token = authentication.oauth2_request

        if not authentication.is_client_only:
            result.update(self.user_token_converter.convert_user_authentication(authentication.user_authentication))
        else:
            if client_token.authorities:
                result[self.AUTHORITIES] = client_token.authorities

        if token.scope:
            result[self.SCOPE] = token.scope
        if self.JTI in token.additional_information:
            result[self.JTI] = token.additional_information[self.JTI]
        if token.expiration:
            result[self.EXP] = int(token.expiration.timestamp())

        result.update(token.additional_information)

        result[self.CLIENT_ID] = client_token.client_id
        if client_token.resource_ids:
            result[self.AUD] = client_token.resource_ids
        return result

    def extract_access_token(self, token_value: str, data: dict) -> OAuth2AccessToken:
        token = OAuth2AccessToken(token_value)
        info = dict(data)
        if self.SCOPE in info:
            info.pop(self.SCOPE)
        if self.EXP in info:
            info.pop(self.EXP)
        if self.CLIENT_ID in info:
            info.pop(self.CLIENT_ID)
        if self.AUD in info:
            info.pop(self.AUD)
        if self.EXP in data:
            token.expiration = dt.datetime.fromtimestamp(data[self.EXP])
        if self.JTI in data:
            info[self.JTI] = data[self.JTI]
        token.scope = self._extract_scope(data)
        token.additional_information = info
        return token

    def extract_authentication(self, data: dict) -> OAuth2Authentication:
        params = {}
        scope = self._extract_scope(data)
        user = self.user_token_converter.extract_authentication(data)
        client_id = data.get(self.CLIENT_ID)
        params[self.CLIENT_ID] = client_id
        resource_ids = self._get_audience(data)
        authorities = None
        if user is None and self.AUTHORITIES in data:
            authorities = set(data[self.AUTHORITIES])
        request = OAuth2Request(request_parameters=params,
                                client_id=client_id,
                                authorities=authorities,
                                approved=True,
                                scope=scope,
                                resource_ids=resource_ids)
        return OAuth2Authentication(request, user_authentication=user)

    def _extract_scope(self, data: dict):
        scope = set()
        if self.SCOPE in data:
            s = data[self.SCOPE]
            if isinstance(s, str):
                scope.update(s.split(' '))
            elif hasattr(s, '__iter__'):
                scope.update(s)
        return scope

    def _get_audience(self, data: dict):
        result = set()
        if self.AUD not in data:
            return result
        auds = data[self.AUD]
        if isinstance(auds, str):
            result.add(auds)
        elif hasattr(auds, '__iter__'):
            result.update(auds)
        return set(auds)


class TokenEnhancer(metaclass=ABCMeta):

    @abstractmethod
    def enhance(self, access_token: OAuth2AccessToken, authentication: OAuth2Authentication) -> OAuth2AccessToken:
        pass


class UserAuthenticationConverter:
    """
    Utility interface for converting a user authentication to and from a dict.
    """

    USERNAME = 'username'
    AUTHORITIES = AccessTokenConverter.AUTHORITIES

    def __init__(self):
        self.default_authorities = set()
        self.user_details_service: UserDetailsService = None

    def convert_user_authentication(self, user_authentication: Authentication) -> dict:
        result = {}
        result[self.USERNAME] = user_authentication.name
        if user_authentication.authorities:
            result[self.AUTHORITIES] = user_authentication.authorities
        return result

    def extract_authentication(self, data: dict) -> Optional[Authentication]:
        if self.USERNAME in data:
            principal = data[self.USERNAME]
            authorities = self._get_authorities(data)
            if self.user_details_service is not None:
                user = self.user_details_service.load_user_by_username(str(principal))
                authorities = user.authorities
                principal = user
            return UserAuthentication(principal, authorities=authorities)

    def _get_authorities(self, data: dict):
        if self.AUTHORITIES not in data:
            return self.default_authorities
        authorities = set(data[self.AUTHORITIES])
        return authorities


class JwtAccessTokenConverter(AccessTokenConverter, TokenEnhancer):
    TOKEN_ID = AccessTokenConverter.JTI
    ACCESS_TOKEN_ID = AccessTokenConverter.ATI

    def __init__(self):
        self.token_converter = DefaultAccessTokenConverter()
        self.signing_algorithm = 'HS256'
        self.signing_key = JwtHelper.generate_jwt_secret()
        self.verifying_key = self.signing_key

    def convert_access_token(self, token: OAuth2AccessToken, authentication: OAuth2Authentication) -> dict:
        return self.token_converter.convert_access_token(token, authentication)

    def extract_access_token(self, token_value: str, data: dict) -> OAuth2AccessToken:
        return self.token_converter.extract_access_token(token_value, data)

    def extract_authentication(self, data: dict) -> OAuth2Authentication:
        return self.token_converter.extract_authentication(data)

    def enhance(self, access_token: OAuth2AccessToken, authentication: OAuth2Authentication) -> OAuth2AccessToken:
        result = access_token.copy()
        info = dict(access_token.additional_information)
        token_id = result.value
        if self.TOKEN_ID not in info:
            info[self.TOKEN_ID] = token_id
        else:
            token_id = str(info[self.TOKEN_ID])
        result.additional_information = info
        result.value = self.encode(result, authentication)

        refresh_token = result.refresh_token
        if refresh_token:
            encoded_refresh_token = access_token.copy()
            encoded_refresh_token.value = refresh_token.value
            encoded_refresh_token.expiration = refresh_token.expiration
            try:
                claims = JwtHelper.decode_jwt(refresh_token.value, self.verifying_key, self.signing_algorithm)
                if self.TOKEN_ID in claims:
                    encoded_refresh_token.value = str(claims[self.TOKEN_ID])
            except Exception:
                pass
            refresh_token_info = dict(access_token.additional_information)
            refresh_token_info[self.TOKEN_ID] = encoded_refresh_token.value
            refresh_token_info[self.ACCESS_TOKEN_ID] = token_id
            encoded_refresh_token.additional_information = refresh_token_info
            token = OAuth2RefreshToken(self.encode(encoded_refresh_token, authentication),
                                       expiration=refresh_token.expiration)
            result.refresh_token = token
        return result

    def encode(self, access_token: OAuth2AccessToken, authentication: OAuth2Authentication) -> str:
        payload = self.token_converter.convert_access_token(access_token, authentication)
        token = JwtHelper.encode_jwt(payload, self.signing_key, self.signing_algorithm)
        return token

    def decode(self, token_value: str) -> dict:
        try:
            payload = JwtHelper.decode_jwt(token_value, self.verifying_key, algorithm=self.signing_algorithm)
        except Exception as e:
            raise InvalidTokenError(e)
        return payload

    def is_refresh_token(self, token):
        return self.ACCESS_TOKEN_ID in token.additional_information

    @property
    def is_public(self):
        if re.match(r'^(RS|ES|PS)\d+$', self.signing_algorithm) is not None:
            return True
        return False

    def get_key(self):
        result = {'alg': self.signing_algorithm,
                  'value': self.verifying_key}
        return result
