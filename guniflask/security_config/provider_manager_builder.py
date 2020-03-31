# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.security_config.security_builder import SecurityBuilder
from guniflask.security.authentication_provider import AuthenticationProvider

__all__ = ['ProviderManagerBuilder']


class ProviderManagerBuilder(SecurityBuilder, metaclass=ABCMeta):
    @abstractmethod
    def with_authentication_provider(self, provider: AuthenticationProvider) -> 'ProviderManagerBuilder':
        pass
