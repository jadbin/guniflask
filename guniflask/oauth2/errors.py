# coding=utf-8

__all__ = ['OAuth2Error',
           'ClientAuthenticationError',
           'InvalidClientError',
           'InvalidTokenError',
           'InvalidGrantError',
           'InvalidScopeError']


class OAuth2Error(Exception):
    """
    OAuth2 exception
    """


class ClientAuthenticationError(OAuth2Error):
    """
    Client authentication exception
    """


class InvalidClientError(ClientAuthenticationError):
    """
    Invalid client exception
    """


class InvalidTokenError(ClientAuthenticationError):
    """
    Invalid token exception
    """


class InvalidGrantError(ClientAuthenticationError):
    """
    Invalid grant exception
    """


class InvalidScopeError(OAuth2Error):
    """
    Invalid scope exception
    """
