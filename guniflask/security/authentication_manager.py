# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.security.authentication import Authentication

__all__ = ['AuthenticationManager']


class AuthenticationManager(metaclass=ABCMeta):
    @abstractmethod
    def authenticate(self, authentication: Authentication) -> Authentication:
        pass
