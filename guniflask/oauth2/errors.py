# coding=utf-8

__all__ = ['OAuth2Error',
           'ClientAuthenticationError',
           'InvalidRequestError',
           'InvalidClientError',
           'InvalidTokenError',
           'InvalidGrantError',
           'InvalidScopeError',
           'OAuth2AccessDeniedError',
           'UnsupportedGrantTypeError',
           'ClientRegistrationError',
           'NoSuchClientError',
           'ClientAlreadyExistsError']


class OAuth2Error(Exception):
    """
    OAuth2 exception
    """


class ClientAuthenticationError(OAuth2Error):
    """
    Client authentication exception
    """


class InvalidRequestError(ClientAuthenticationError):
    """
    Invalid request exception
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


class OAuth2AccessDeniedError(OAuth2Error):
    """
    OAuth2 access denied
    """


class UnsupportedGrantTypeError(OAuth2Error):
    """
    Unsupported grant type exception
    """


class ClientRegistrationError(Exception):
    """
    Client registration exception
    """


class NoSuchClientError(ClientRegistrationError):
    """
    No such client exception
    """


class ClientAlreadyExistsError(ClientRegistrationError):
    """
    Client already exists exception
    """
