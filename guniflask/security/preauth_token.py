# coding=utf-8

from guniflask.security.authentication_token import AuthenticationToken

__all__ = ['PreAuthenticatedToken']


class PreAuthenticatedToken(AuthenticationToken):
    def __init__(self, token):
        super().__init__()
        self._token = token

    @property
    def principal(self):
        return self._token

    @property
    def credentials(self):
        return None
