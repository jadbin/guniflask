# coding=utf-8

from abc import ABCMeta, abstractmethod
from typing import Union

from guniflask.security.authentication import Authentication

__all__ = ['AuthenticationManager']


class AuthenticationManager(metaclass=ABCMeta):
    @abstractmethod
    def authenticate(self, authentication: Authentication) -> Union[Authentication, None]:
        pass
