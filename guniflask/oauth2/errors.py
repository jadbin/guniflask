# coding=utf-8

__all__ = ['OAuth2Error',
           'ClientAuthenticationError',
           'InvalidClientError',
           'InvalidTokenError']


class OAuth2Error(Exception):
    """
    OAuth2 Exception
    """


class ClientAuthenticationError(OAuth2Error):
    """
    Client Authentication Exception
    """


class InvalidClientError(ClientAuthenticationError):
    """
    Invalid Client Exception
    """


class InvalidTokenError(ClientAuthenticationError):
    """
    Invalid token error
    """