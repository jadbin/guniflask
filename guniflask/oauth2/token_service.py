# coding=utf-8

import datetime as dt

from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.token import OAuth2AccessToken
from guniflask.oauth2.token_store import TokenStore
from guniflask.oauth2.token_converter import TokenEnhancer
from guniflask.oauth2.client_details_service import ClientDetailsService

__all__ = ['TokenServices']


class TokenServices:
    """
    Base implementation for token services using random UUID values for the access token and refresh token values.
    """

    def __init__(self):
        self.token_store: TokenStore = None
        self.token_enhancer: TokenEnhancer = None
        self.client_details_service: ClientDetailsService = None
        self.access_token_expires_in = dt.timedelta(days=1)
        self.refresh_token_expires_in = dt.timedelta(days=365)

    def create_access_token(self, authentication: OAuth2Authentication = None) -> OAuth2AccessToken:
        # TODO
        pass

    def refresh_access_token(self, refresh_token_value, token_request) -> OAuth2AccessToken:
        # TODO
        pass

    def get_access_token(self, authentication) -> OAuth2AccessToken:
        return self.token_store.get_access_token(authentication)

    def load_authentication(self, access_token_value) -> OAuth2Authentication:
        # TODO
        pass

    def read_access_token(self, access_token_value) -> OAuth2AccessToken:
        return self.token_store.read_access_token(access_token_value)

    def revoke_token(self, access_token_value):
        access_token = self.token_store.read_access_token(access_token_value)
        if access_token:
            if access_token.refresh_token:
                self.token_store.remove_refresh_token(access_token.refresh_token)
            self.token_store.remove_access_token(access_token)
