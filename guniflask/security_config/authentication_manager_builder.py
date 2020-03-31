# coding=utf-8

from typing import Any, List

from guniflask.security_config.configured_security_builder import ConfiguredSecurityBuilder
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.user_details_service import UserDetailsService
from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.security.provider_manager import ProviderManager
from guniflask.security_config.provider_manager_builder import ProviderManagerBuilder
from guniflask.security_config.dao_authentication_configurer import DaoAuthenticationConfigurer

__all__ = ['AuthenticationManagerBuilder']


class AuthenticationManagerBuilder(ConfiguredSecurityBuilder, ProviderManagerBuilder):
    def __init__(self):
        super().__init__()
        self._parent_authentication_manager: AuthenticationManager = None
        self._authentication_providers: List[AuthenticationProvider] = []
        self._default_user_details_service: UserDetailsService = None

    def _perform_build(self) -> Any:
        provider_manager = ProviderManager(parent=self._parent_authentication_manager,
                                           providers=self._authentication_providers)
        return provider_manager

    @property
    def default_user_details_service(self) -> UserDetailsService:
        return self._default_user_details_service

    def with_authentication_provider(self, provider: AuthenticationProvider) -> 'AuthenticationManagerBuilder':
        self._authentication_providers.append(provider)
        return self

    def with_parent_authentication_manager(
            self, authentication_manager: AuthenticationManager
    ) -> 'AuthenticationManagerBuilder':
        self._parent_authentication_manager = authentication_manager
        return self

    def with_user_details_service(self, user_details_service: UserDetailsService) -> DaoAuthenticationConfigurer:
        self._default_user_details_service = user_details_service
        return self.apply(DaoAuthenticationConfigurer(user_details_service))
