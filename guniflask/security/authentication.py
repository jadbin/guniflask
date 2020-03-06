# coding=utf-8

from guniflask.security.request import OAuth2Request

__all__ = ['Authentication', 'OAuth2Authentication', 'UserAuthentication', 'PreAuthenticatedToken']


class Authentication:
    def __init__(self, authorities=None):
        self._authorities = set()
        if authorities is not None:
            self._authorities.update(authorities)
        self._details = None
        self._authenticated = False

    @property
    def principal(self):
        raise NotImplemented

    @property
    def credentials(self):
        raise NotImplemented

    def authenticate(self, value):
        self._authenticated = value

    @property
    def is_authenticated(self):
        return self._authenticated

    @property
    def authorities(self):
        return self._authorities

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, details):
        self._details = details


class UserAuthentication(Authentication):
    def __init__(self, principal, credentials=None, authorities=None):
        super().__init__(authorities=authorities)
        self._principal = principal
        self._credentials = credentials

    @property
    def principal(self):
        return self._principal

    @property
    def credentials(self):
        return self._credentials


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


class PreAuthenticatedToken(Authentication):
    def __init__(self, token):
        super().__init__()
        self._token = token

    @property
    def principal(self):
        return self._token

    @property
    def credentials(self):
        return None
