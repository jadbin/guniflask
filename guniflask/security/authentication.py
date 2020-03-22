# coding=utf-8

__all__ = ['Authentication', 'UserAuthentication']


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
