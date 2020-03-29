# coding=utf-8

__all__ = ['AuthenticationError',
           'BadCredentialsError',
           'ProviderNotFoundError']


class AuthenticationError(Exception):
    """
    Authentication exception
    """


class BadCredentialsError(AuthenticationError):
    """
    Bad credentials exception
    """


class ProviderNotFoundError(AuthenticationError):
    """
    Provider not found exception
    """
