from flask import current_app

from guniflask.config.app_settings import settings
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.authentication_provider import AuthenticationProvider
from guniflask.security_config.authentication_manager_builder import AuthenticationManagerBuilder
from guniflask.security_config.cors_configurer import CorsConfigurer
from guniflask.security_config.http_basic_configurer import HttpBasicConfigurer
from guniflask.security_config.http_security_builder import HttpSecurityBuilder
from guniflask.web.request_filter import RequestFilter, RequestFilterChain


class HttpSecurity(HttpSecurityBuilder):
    def __init__(self, authentication_builder: AuthenticationManagerBuilder,
                 shared_objects: dict = None):
        super().__init__()
        assert authentication_builder is not None, 'Authentication builder is required'
        self.set_shared_object(AuthenticationManagerBuilder, authentication_builder)
        for k, v in shared_objects.items():
            self.set_shared_object(k, v)
        self._security_filter_chain = RequestFilterChain()
        self._blueprints = []

    def _perform_build(self):
        app = current_app._get_current_object()
        app.before_request(self._security_filter_chain.before_request)
        app.after_request(self._security_filter_chain.after_request)

    def _before_configure(self):
        cors = settings.get_by_prefix('guniflask.cors')
        if cors is not None:
            self.cors(cors)

        self.set_shared_object(AuthenticationManager, self._get_authentication_registry().build())

    def with_authentication_provider(self, authentication_provider: AuthenticationProvider) -> 'HttpSecurity':
        self._get_authentication_registry().with_authentication_provider(authentication_provider)
        return self

    def _get_authentication_registry(self) -> AuthenticationManagerBuilder:
        return self.get_shared_object(AuthenticationManagerBuilder)

    def http_basic(self) -> HttpBasicConfigurer:
        return self._get_or_apply(HttpBasicConfigurer())

    def cors(self, config) -> CorsConfigurer:
        return self._get_or_apply(CorsConfigurer(config))

    def _get_or_apply(self, configurer):
        existing = self.get_configurer(type(configurer))
        if existing:
            return existing
        return self.apply(configurer)

    def add_request_filter(self, request_filter: RequestFilter) -> 'HttpSecurity':
        self._security_filter_chain.add_request_filter(request_filter)
        return self
