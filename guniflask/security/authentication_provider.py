# coding=utf-8

from abc import ABCMeta, abstractmethod
from typing import Type, Optional

from guniflask.security.authentication import Authentication

__all__ = ['AuthenticationProvider']


class AuthenticationProvider(metaclass=ABCMeta):
    @abstractmethod
    def authenticate(self, authentication: Authentication) -> Optional[Authentication]:
        pass

    @abstractmethod
    def supports(self, authentication_cls: Type[Authentication]) -> bool:
        pass
