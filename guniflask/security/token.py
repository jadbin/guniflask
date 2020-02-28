# coding=utf-8

import datetime as dt
from datetime import datetime

from guniflask.security.authentication import Authentication, OAuth2Authentication

__all__ = ['AccessToken', 'RefreshToken',
           'AccessTokenConverter', 'UserAuthenticationConverter', 'TokenEnhancer',
           'TokenService', 'TokenStore']


class RefreshToken:
    """
    OAuth2 refresh token
    """

    def __init__(self, value: str, expiration: datetime = None):
        self.value = value
        self.expiration = expiration


class AccessToken:
    """
    OAuth2 access token
    """

    BEARER_TYPE = 'Bearer'
    TOKEN_TYPE = 'token_type'
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'
    EXPIRES_IN = 'expires_in'
    SCOPE = 'scope'

    def __init__(self, value, refresh_token: RefreshToken = None, expiration: datetime = None, scope=None,
                 additional_info=None):
        self.value = value
        self.token_type = self.BEARER_TYPE.lower()
        self.refresh_token = refresh_token
        self.expiration = expiration
        self.scope = set()
        if scope is not None:
            self.scope.update(scope)
        self.additional_info = dict()
        if additional_info is not None:
            self.additional_info.update(additional_info)

    def __str__(self):
        return str(self.to_dict())

    @property
    def expires_in(self):
        if self.expiration is None:
            return 0
        return int(self.expiration.timestamp() - datetime.now().timestamp())

    def to_dict(self):
        res = {self.ACCESS_TOKEN: self.value, self.TOKEN_TYPE: self.token_type}
        if self.refresh_token is not None:
            res[self.REFRESH_TOKEN] = self.refresh_token.value
        if self.expiration is not None:
            res[self.EXPIRES_IN] = self.expires_in
        if self.scope is not None:
            res[self.SCOPE] = ' '.join(self.scope)
        if self.additional_info is not None:
            res.update(self.additional_info)
        return res


class AccessTokenConverter:
    """
    Converter interface for token service implementations that store authentication data inside the token.
    """

    AUD = 'aud'
    CLIENT_ID = 'client_id'
    EXP = 'exp'
    JTI = 'jti'
    ATI = 'ati'
    SCOPE = AccessToken.SCOPE
    AUTHORITIES = 'authorities'

    def convert_access_token(self, access_token: AccessToken, authentication: OAuth2Authentication):
        # TODO
        pass

    def extract_access_token(self, token_value: str, data):
        # TODO
        pass

    def extract_authentication(self, data):
        # TODO
        pass


class TokenEnhancer:
    def enhance(self, access_token: AccessToken, authentication: OAuth2Authentication) -> AccessToken:
        raise NotImplemented


class UserAuthenticationConverter:
    """
    Utility interface for converting a user authentication to and from a Map.
    """

    USERNAME = 'user_name'

    def convert_user_authentication(self, user_authentication: Authentication):
        # TODO
        pass

    def extract_authentication(self, data):
        # TODO
        pass


class TokenService:
    """
    Base implementation for token services using random UUID values for the access token and refresh token values.
    """

    def __init__(self):
        self.token_store = None
        self.token_converter = None
        self.client_details_service = None

    def init_app(self, app):
        app.config.setdefault('ACCESS_TOKEN_EXPIRES_IN', dt.timedelta(days=1))
        app.config.setdefault('REFRESH_TOKEN_EXPIRES_IN', dt.timedelta(days=365))

    def create_access_token(self, authentication: OAuth2Authentication = None) -> AccessToken:
        # TODO
        pass

    def refresh_access_token(self, refresh_token_value, token_request) -> AccessToken:
        # TODO
        pass

    def get_access_token(self, authentication) -> AccessToken:
        return self.token_store.get_access_token(authentication)

    def load_authentication(self, access_token_value) -> OAuth2Authentication:
        # TODO
        pass

    def read_access_token(self, access_token_value) -> AccessToken:
        return self.token_store.read_access_token(access_token_value)

    def revoke_token(self, access_token_value):
        access_token = self.token_store.read_access_token(access_token_value)
        if access_token:
            if access_token.refresh_token:
                self.token_store.remove_refresh_token(access_token.refresh_token)
            self.token_store.remove_access_token(access_token)


class TokenStore:
    """
    Persistence interface for OAuth2 tokens.
    """

    def read_authentication(self, access_token: AccessToken):
        raise NotImplemented

    def store_access_token(self, access_token: AccessToken, authentication: OAuth2Authentication):
        raise NotImplemented

    def read_access_token(self, access_token_value: str):
        raise NotImplemented

    def remove_access_token(self, access_token: AccessToken):
        raise NotImplemented

    def store_refresh_token(self, refresh_token: str, authentication: OAuth2Authentication):
        raise NotImplemented

    def read_refresh_token(self, refresh_token_value: str):
        raise NotImplemented

    def read_authentication_for_refresh_token(self, refresh_token: RefreshToken):
        raise NotImplemented

    def remove_refresh_token(self, refresh_token: RefreshToken):
        raise NotImplemented

    def remove_access_token_using_refresh_token(self, refresh_token: RefreshToken):
        raise NotImplemented

    def get_access_token(self, authentication: OAuth2Authentication):
        raise NotImplemented

    def find_tokens_by_client_id_and_username(self, client_id: str, username: str):
        raise NotImplemented

    def find_tokens_by_client_id(self, client_id: str):
        raise NotImplemented
