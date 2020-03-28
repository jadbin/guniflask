# coding=utf-8

__all__ = ['AuthenticationError',
           'BadCredentialsError']


class AuthenticationError(Exception):
    """
    Authentication exception
    """


class BadCredentialsError(AuthenticationError):
    """
    Bad credentials exception
    """
