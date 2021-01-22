from typing import Any, List, Optional

from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.security.provider_manager import ProviderManager
from guniflask.security_config.configured_security_builder import ConfiguredSecurityBuilder
from guniflask.security_config.provider_manager_builder import ProviderManagerBuilder


class AuthenticationManagerBuilder(ConfiguredSecurityBuilder, ProviderManagerBuilder):
    def __init__(self):
        super().__init__()
        self._parent_authentication_manager: Optional[AuthenticationManager] = None
        self._authentication_providers: List[AuthenticationProvider] = []

    def _perform_build(self) -> Any:
        provider_manager = ProviderManager(parent=self._parent_authentication_manager,
                                           providers=self._authentication_providers)
        return provider_manager

    def with_authentication_provider(self, provider: AuthenticationProvider) -> 'AuthenticationManagerBuilder':
        self._authentication_providers.append(provider)
        return self

    def with_parent_authentication_manager(
            self, authentication_manager: AuthenticationManager
    ) -> 'AuthenticationManagerBuilder':
        self._parent_authentication_manager = authentication_manager
        return self
