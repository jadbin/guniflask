# coding=utf-8

from typing import List

from flask import current_app

from guniflask.security_config.security_builder import SecurityBuilder
from guniflask.security_config.web_security_builder import WebSecurityBuilder
from guniflask.web.request_filter import RequestFilter
from guniflask.security_config.http_basic_configurer import HttpBasicConfigurer
from guniflask.security_config.cors_configurer import CorsConfigurer

__all__ = ['WebSecurity']


class WebSecurity(WebSecurityBuilder):
    def __init__(self):
        super().__init__()
        self._before_request_filters: List[RequestFilter] = []
        self._after_request_filters: List[RequestFilter] = []
        self._http_security_builders: List[SecurityBuilder] = []

    def _perform_build(self):
        for f in self._before_request_filters:
            current_app.before_request(f.before_request)
        for f in self._after_request_filters:
            current_app.after_request(f.after_request)
        for builder in self._http_security_builders:
            builder.build()

    def add_http_security_builder(self, security_builder: SecurityBuilder):
        self._http_security_builders.append(security_builder)

    def add_request_filter(self, request_filter: RequestFilter):
        self.add_before_request_filter(request_filter)
        self.add_after_request_filter(request_filter)

    def add_before_request_filter(self, request_filter: RequestFilter):
        self._before_request_filters.append(request_filter)

    def add_after_request_filter(self, request_filter: RequestFilter):
        self._after_request_filters.append(request_filter)

    def http_basic(self):
        return self._get_or_apply(HttpBasicConfigurer())

    def cors(self, config):
        return self._get_or_apply(CorsConfigurer(config))

    def _get_or_apply(self, configurer):
        existing = self.get_configurer(configurer)
        if existing:
            return existing
        return self.apply(configurer)
