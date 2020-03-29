# coding=utf-8

from guniflask.security.authentication_token import AuthenticationToken

__all__ = ['PreAuthenticatedToken']


class PreAuthenticatedToken(AuthenticationToken):
    def __init__(self, principal, credentials=None, authorities=None):
        super().__init__(authorities=authorities)
        self._principal = principal
        self._credentials = credentials
        if authorities is not None:
            self.authenticate(True)

    @property
    def principal(self):
        return self._principal

    @property
    def credentials(self):
        return self._credentials
