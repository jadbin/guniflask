# coding=utf-8

from typing import Mapping

from guniflask.security.authentication import Authentication, OAuth2Authentication
from guniflask.security.token import OAuth2AccessToken

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


class TokenEnhancer:
    def enhance(self, access_token: OAuth2AccessToken, authentication: OAuth2Authentication) -> OAuth2AccessToken:
        raise NotImplemented


class UserAuthenticationConverter:
    """
    Utility interface for converting a user authentication to and from a Map.
    """

    USERNAME = 'username'

    def convert_user_authentication(self, user_authentication: Authentication):
        # TODO
        pass

    def extract_authentication(self, data):
        # TODO
        pass


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
