# coding=utf-8

from typing import Any, List

from guniflask.security_config.configured_security_builder import ConfiguredSecurityBuilder
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.user_details_service import UserDetailsService
from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.security.provider_manager import ProviderManager

__all__ = ['AuthenticationManagerBuilder']


class AuthenticationManagerBuilder(ConfiguredSecurityBuilder):
    def __init__(self):
        super().__init__()
        self.parent_authentication_manager: AuthenticationManager = None
        self._authentication_providers: List[AuthenticationProvider] = []
        self.default_user_details_service: UserDetailsService = None

    def _perform_build(self) -> Any:
        provider_manager = ProviderManager(parent=self.parent_authentication_manager,
                                           providers=self._authentication_providers)
        return provider_manager

    def get_default_user_details_service(self) -> UserDetailsService:
        return self.default_user_details_service

    def add_authentication_provider(self, provider: AuthenticationProvider):
        self._authentication_providers.append(provider)
