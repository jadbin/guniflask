# coding=utf-8

from guniflask.security.authentication import Authentication

__all__ = ['PreAuthenticatedToken']


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
