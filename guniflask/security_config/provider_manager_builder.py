from abc import ABCMeta, abstractmethod

from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.security_config.security_builder import SecurityBuilder


class ProviderManagerBuilder(SecurityBuilder, metaclass=ABCMeta):
    @abstractmethod
    def with_authentication_provider(self, provider: AuthenticationProvider) -> 'ProviderManagerBuilder':
        pass  # pragma: no cover
