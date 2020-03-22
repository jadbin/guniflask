# coding=utf-8

__all__ = ['UserDetails']


class UserDetails:
    def __init__(self, username=None, authorities=None):
        self._username = username
        self._authorities = set()
        if authorities:
            self._authorities.update(authorities)

    @property
    def username(self):
        return self._username

    @property
    def authorities(self):
        return self._authorities
