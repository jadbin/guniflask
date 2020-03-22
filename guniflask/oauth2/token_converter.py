# coding=utf-8

from typing import Mapping, Union
from abc import ABCMeta, abstractmethod

from guniflask.security.authentication import Authentication
from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.user_details_service import UserDetailsService
from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.token import OAuth2AccessToken

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

    def convert_access_token(self, access_token: OAuth2AccessToken, authentication: OAuth2Authentication) -> Mapping:
        # TODO
        pass

    def extract_access_token(self, token_value: str, data: Mapping) -> OAuth2AccessToken:
        # TODO
        pass

    def extract_authentication(self, data: Mapping) -> OAuth2Authentication:
        # TODO
        pass


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
            result[self.AUTHORITIES] = set(user_authentication.authorities)
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
        authorities = set()
        authorities.update(data[self.AUTHORITIES])
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
