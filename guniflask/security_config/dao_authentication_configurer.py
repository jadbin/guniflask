# coding=utf-8

from guniflask.security_config.provider_manager_builder import ProviderManagerBuilder
from guniflask.security_config.user_details_aware_configurer import UserDetailsAwareConfigurer
from guniflask.security.user_details_service import UserDetailsService
from guniflask.security.password_encoder import PasswordEncoder
from guniflask.security.dao_authentication_provider import DaoAuthenticationProvider

__all__ = ['DaoAuthenticationConfigurer']


class DaoAuthenticationConfigurer(UserDetailsAwareConfigurer):

    def __init__(self, user_details_service: UserDetailsService):
        super().__init__()
        self._user_details_service = user_details_service
        self._provider = DaoAuthenticationProvider()
        self._provider.user_details_service = user_details_service

    @property
    def user_details_service(self) -> UserDetailsService:
        return self._user_details_service

    def configure(self, builder: ProviderManagerBuilder):
        builder.with_authentication_provider(self._provider)

    def with_password_encoder(self, password_encoder: PasswordEncoder) -> 'DaoAuthenticationConfigurer':
        self._provider.password_encoder = password_encoder
        return self
