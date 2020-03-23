# coding=utf-8

from guniflask.security.authentication import Authentication
from guniflask.security.authentication_token import AuthenticationToken
from guniflask.oauth2.request import OAuth2Request

__all__ = ['OAuth2Authentication']


class OAuth2Authentication(AuthenticationToken):
    def __init__(self, oauth2_request: OAuth2Request, user_authentication: Authentication = None):
        authorities = None
        if user_authentication is not None:
            authorities = user_authentication.authorities
        super().__init__(authorities=authorities)
        self._oauth2_request = oauth2_request
        self._user_authentication = user_authentication

    @property
    def principal(self):
        if self._user_authentication is None:
            return self._oauth2_request.client_id
        return self.user_authentication.principal

    @property
    def credentials(self):
        return None

    @property
    def oauth2_request(self):
        return self._oauth2_request

    @property
    def user_authentication(self):
        return self._user_authentication

    @property
    def is_client_only(self):
        return self._user_authentication is None
