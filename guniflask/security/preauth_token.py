# coding=utf-8

from guniflask.security.authentication_token import AuthenticationToken

__all__ = ['PreAuthenticatedToken']


class PreAuthenticatedToken(AuthenticationToken):
    def __init__(self, principal, authorities=None):
        super().__init__(authorities=authorities)
        self._principal = principal

    @property
    def principal(self):
        return self._principal

    @property
    def credentials(self):
        return None
