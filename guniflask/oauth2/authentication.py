# coding=utf-8

from guniflask.security.authentication import Authentication
from guniflask.oauth2.request import OAuth2Request

__all__ = ['OAuth2Authentication']


class OAuth2Authentication(Authentication):
    def __init__(self, stored_request: OAuth2Request, user_authentication: Authentication = None):
        authorities = None
        if user_authentication is not None:
            authorities = user_authentication.authorities
        super().__init__(authorities=authorities)
        self._stored_request = stored_request
        self._user_authentication = user_authentication

    @property
    def principal(self):
        if self._user_authentication is None:
            return self._stored_request.client_id
        return self.user_authentication.principal

    @property
    def credentials(self):
        return None

    @property
    def stored_request(self):
        return self._stored_request

    @property
    def user_authentication(self):
        return self._user_authentication
