# coding=utf-8

from guniflask.security.authentication import Authentication

__all__ = ['AuthenticationManager']


class AuthenticationManager:
    def authenticate(self, authentication: Authentication) -> Authentication:
        raise NotImplemented
