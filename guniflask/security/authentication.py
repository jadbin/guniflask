# coding=utf-8

from abc import ABCMeta, abstractmethod

__all__ = ['Authentication']


class Authentication(metaclass=ABCMeta):
    def __init__(self, authorities=None):
        self._authorities = set()
        if authorities is not None:
            self._authorities.update(authorities)
        self._authenticated = False
        self.details = None

    @property
    @abstractmethod
    def name(self):
        raise NotImplemented

    @property
    @abstractmethod
    def principal(self):
        raise NotImplemented

    @property
    @abstractmethod
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
