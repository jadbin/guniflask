# coding=utf-8

from flask import current_app

from guniflask.security_config.http_security_builder import HttpSecurityBuilder
from guniflask.security_config.authentication_manager_builder import AuthenticationManagerBuilder
from guniflask.security.user_details_service import UserDetailsService
from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.web.request_filter import RequestFilter
from guniflask.security_config.http_basic_configurer import HttpBasicConfigurer
from guniflask.security_config.cors_configurer import CorsConfigurer
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security_config.security_filter_chain import SecurityFilterChain

__all__ = ['HttpSecurity']


class HttpSecurity(HttpSecurityBuilder):
    def __init__(self, authentication_builder: AuthenticationManagerBuilder,
                 shared_objects: dict = None):
        super().__init__()
        assert authentication_builder is not None, 'Authentication builder is required'
        self.set_shared_object(AuthenticationManagerBuilder, authentication_builder)
        for k, v in shared_objects.items():
            self.set_shared_object(k, v)
        self._security_filter_chain = SecurityFilterChain()
        self._blueprints = []

    def _perform_build(self):
        if not self._blueprints:
            self._blueprints = [current_app]
        for b in self._blueprints:
            b.before_request(self._security_filter_chain.before_request)
            b.after_request(self._security_filter_chain.after_request)

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
        existing = self.get_configurer(type(configurer))
        if existing:
            return existing
        return self.apply(configurer)

    def add_request_filter(self, request_filter: RequestFilter):
        self._security_filter_chain.add_request_filter(request_filter)

    def add_blueprint(self, blueprint):
        self._blueprints.append(blueprint)
