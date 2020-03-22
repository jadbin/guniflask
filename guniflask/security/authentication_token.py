# coding=utf-8

from guniflask.security.authentication import Authentication
from guniflask.security.user_details import UserDetails

__all__ = ['AuthenticationToken', 'UserAuthentication']


class AuthenticationToken(Authentication):
    @property
    def name(self):
        if isinstance(self.principal, UserDetails):
            return self.principal.username
        if self.principal is None:
            return ''
        return str(self.principal)


class UserAuthentication(AuthenticationToken):
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
