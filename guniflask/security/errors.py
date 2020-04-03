# coding=utf-8

__all__ = ['AuthenticationError',
           'BadCredentialsError',
           'ProviderNotFoundError',
           'UsernameNotFoundError',
           'InsufficientAuthenticationError']


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


class UsernameNotFoundError(AuthenticationError):
    """
    Username not found exception
    """


class InsufficientAuthenticationError(AuthenticationError):
    """
    Insufficient authentication exception
    """
