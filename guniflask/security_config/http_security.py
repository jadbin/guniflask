# coding=utf-8

from guniflask.security_config.http_security_builder import HttpSecurityBuilder
from guniflask.security_config.authentication_manager_builder import AuthenticationManagerBuilder
from guniflask.security.user_details_service import UserDetailsService
from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.web.request_filter import RequestFilter
from guniflask.security_config.web_security import WebSecurity
from guniflask.security_config.http_basic_configurer import HttpBasicConfigurer
from guniflask.security_config.cors_configurer import CorsConfigurer
from guniflask.security.authentication_manager import AuthenticationManager

__all__ = ['HttpSecurity']


class HttpSecurity(HttpSecurityBuilder):
    def __init__(self, authentication_builder: AuthenticationManagerBuilder):
        super().__init__()
        assert authentication_builder is not None, 'Authentication builder is required'
        self.set_shared_object(AuthenticationManagerBuilder, authentication_builder)

    def _perform_build(self):
        pass

    def _before_configure(self):
        self.set_shared_object(AuthenticationManager, self._get_authentication_registry().build())

    def with_user_details_service(self, user_details_service: UserDetailsService) -> 'HttpSecurity':
        self._get_authentication_registry().with_user_details_service(user_details_service)
        return self

    def with_authentication_provider(self, authentication_provider: AuthenticationProvider) -> 'HttpSecurity':
        self._get_authentication_registry().with_authentication_provider(authentication_provider)
        return self

    def _get_authentication_registry(self) -> AuthenticationManagerBuilder:
        return self.get_shared_object(AuthenticationManagerBuilder)

    def http_basic(self):
        return self._get_or_apply(HttpBasicConfigurer())

    def cors(self, config):
        return self._get_or_apply(CorsConfigurer(config))

    def _get_or_apply(self, configurer):
        existing = self.get_configurer(configurer)
        if existing:
            return existing
        return self.apply(configurer)

    def add_request_filter(self, request_filter: RequestFilter):
        web_security: WebSecurity = self.get_shared_object(WebSecurity)
        web_security.add_request_filter(request_filter)
