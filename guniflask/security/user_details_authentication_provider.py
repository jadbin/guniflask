# coding=utf-8

from abc import ABCMeta, abstractmethod
from typing import Union, Type
import inspect

from guniflask.security.authentication import Authentication
from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.errors import UsernameNotFoundError, AuthenticationError
from guniflask.security.user_details import UserDetails

__all__ = ['UserDetailsAuthenticationProvider']


class UserDetailsAuthenticationProvider(AuthenticationProvider, metaclass=ABCMeta):

    @abstractmethod
    def retrieve_user(self, username: str, authentication: UserAuthentication) -> UserDetails:
        pass

    @abstractmethod
    def check_authentication(self, user_details: UserDetails, authentication: UserAuthentication):
        pass

    def authenticate(self, authentication: Authentication) -> Union[Authentication, None]:
        assert isinstance(authentication, UserAuthentication)
        username = authentication.name
        user = None
        try:
            user = self.retrieve_user(username, authentication)
        except UsernameNotFoundError:
            pass

        self.check_authentication(user, authentication)

        return UserAuthentication(user, credentials=authentication.credentials, authorities=user.authorities)

    def supports(self, authentication_cls: Type[Authentication]) -> bool:
        return inspect.isclass(authentication_cls) and issubclass(authentication_cls, UserAuthentication)
