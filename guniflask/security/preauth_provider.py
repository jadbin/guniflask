# coding=utf-8

from typing import Type
import inspect

from guniflask.security.authentication import Authentication
from guniflask.security.preauth_token import PreAuthenticatedToken
from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.security.authentication_user_details_service import AuthenticationUserDetailsService

__all__ = ['PreAuthenticatedProvider']


class PreAuthenticatedProvider(AuthenticationProvider):
    def __init__(self, user_details_service: AuthenticationUserDetailsService):
        self.pre_authenticated_user_details_service = user_details_service

    def authenticate(self, authentication: Authentication):
        if not self.supports(type(authentication)):
            return
        if authentication.principal is None:
            return
        if authentication.credentials is None:
            return
        user_details = self.pre_authenticated_user_details_service.load_user_details(authentication)
        result = PreAuthenticatedToken(user_details, authentication.credentials, user_details.authorities)
        result.details = authentication.details
        return result

    def supports(self, authentication_cls: Type[Authentication]) -> bool:
        return inspect.isclass(authentication_cls) and issubclass(authentication_cls, PreAuthenticatedToken)
