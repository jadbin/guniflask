# coding=utf-8

from typing import Union, Collection

from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.token import OAuth2AccessToken, OAuth2RefreshToken
from guniflask.oauth2.errors import InvalidTokenError
from guniflask.oauth2.token_converter import JwtAccessTokenConverter

__all__ = ['TokenStore', 'JwtTokenStore']


class TokenStore:
    """
    Persistence interface for OAuth2 tokens.
    """

    def read_authentication(self, access_token: Union[OAuth2AccessToken, str]) -> OAuth2AccessToken:
        raise NotImplemented

    def store_access_token(self, access_token: OAuth2AccessToken, authentication: OAuth2Authentication):
        raise NotImplemented

    def read_access_token(self, access_token_value: str) -> OAuth2AccessToken:
        raise NotImplemented

    def remove_access_token(self, access_token: OAuth2AccessToken):
        raise NotImplemented

    def store_refresh_token(self, refresh_token: str, authentication: OAuth2Authentication):
        raise NotImplemented

    def read_refresh_token(self, refresh_token_value: str) -> OAuth2RefreshToken:
        raise NotImplemented

    def read_authentication_for_refresh_token(self, refresh_token: OAuth2RefreshToken) -> OAuth2Authentication:
        raise NotImplemented

    def remove_refresh_token(self, refresh_token: OAuth2RefreshToken):
        raise NotImplemented

    def remove_access_token_using_refresh_token(self, refresh_token: OAuth2RefreshToken):
        raise NotImplemented

    def get_access_token(self, authentication: OAuth2Authentication) -> OAuth2AccessToken:
        raise NotImplemented

    def find_tokens_by_client_id_and_username(self, client_id: str, username: str) -> Collection:
        raise NotImplemented

    def find_tokens_by_client_id(self, client_id: str) -> Collection:
        raise NotImplemented


class JwtTokenStore(TokenStore):
    def __init__(self):
        self.jwt_token_converter: JwtAccessTokenConverter = None

    def read_authentication(self, access_token):
        if isinstance(access_token, OAuth2AccessToken):
            access_token = access_token.value
        return self.jwt_token_converter.extract_authentication(self.jwt_token_converter.decode(access_token))

    def store_access_token(self, access_token, authentication):
        return None

    def read_access_token(self, access_token_value):
        access_token = self._convert_access_token(access_token_value)
        if self.jwt_token_converter.is_refresh_token(access_token):
            raise InvalidTokenError('Encoded token is a refresh token')
        return access_token

    def remove_access_token(self, access_token):
        return None

    def store_refresh_token(self, refresh_token, authentication):
        return None

    def read_refresh_token(self, refresh_token_value):
        # TODO
        pass

    def read_authentication_for_refresh_token(self, refresh_token):
        return self.read_authentication(refresh_token.value)

    def remove_refresh_token(self, refresh_token):
        return None

    def remove_access_token_using_refresh_token(self, refresh_token):
        return None

    def get_access_token(self, authentication):
        return None

    def find_tokens_by_client_id_and_username(self, client_id, username):
        return []

    def find_tokens_by_client_id(self, client_id):
        return []

    def _convert_access_token(self, access_token_value):
        return self.jwt_token_converter.extract_access_token(access_token_value,
                                                             self.jwt_token_converter.decode(access_token_value))
