# coding=utf-8

from typing import Union
from abc import ABCMeta, abstractmethod
import datetime as dt

from guniflask.security.authentication import Authentication
from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.user_details_service import UserDetailsService
from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.token import OAuth2AccessToken
from guniflask.oauth2.request import OAuth2Request

__all__ = ['AccessTokenConverter', 'TokenEnhancer', 'UserAuthenticationConverter',
           'JwtAccessTokenConverter']


class AccessTokenConverter:
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
        if self.JTI in token.additional_info:
            result[self.JTI] = token.additional_info[self.JTI]
        if token.expiration:
            result[self.EXP] = int(token.expiration.timestamp())

        result.update(token.additional_info)

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
            token.expiration = dt.datetime.utcfromtimestamp(data[self.EXP]).astimezone()
        if self.JTI in data:
            info[self.JTI] = data[self.JTI]
        token.scope = self._extract_scope(data)
        token.additional_info = info
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

    def extract_authentication(self, data: dict) -> Union[Authentication, None]:
        if self.USERNAME in data:
            principal = data[self.USERNAME]
            authorities = self._get_authorities(data)
            if self.user_details_service is not None:
                user = self.user_details_service.load_user_by_username(str(principal))
                authorities = user.authorities
                principal = user
            return UserAuthentication(principal, authorities)

    def _get_authorities(self, data: dict):
        if self.AUTHORITIES not in data:
            return self.default_authorities
        authorities = set(data[self.AUTHORITIES])
        return authorities


class JwtAccessTokenConverter(AccessTokenConverter, TokenEnhancer):
    TOKEN_ID = AccessTokenConverter.JTI
    ACCESS_TOKEN_ID = AccessTokenConverter.ATI

    def convert_access_token(self, access_token, authentication):
        # TODO
        pass

    def extract_access_token(self, token_value, data):
        # TODO
        pass

    def extract_authentication(self, data):
        # TODO
        pass

    def _enhance(self, access_token, authentication):
        # TODO
        pass

    def _encode(self, access_token, authentication):
        # TODO
        pass

    def _decode(self, token_value):
        # TODO
        pass

    def is_refresh_token(self, token):
        return self.ACCESS_TOKEN_ID in token.additional_information()
