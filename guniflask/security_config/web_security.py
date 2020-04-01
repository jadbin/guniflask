# coding=utf-8

from typing import Dict, TypeVar, List
from functools import update_wrapper

from flask import current_app, request

from guniflask.security_config.security_builder import SecurityBuilder
from guniflask.security_config.configured_security_builder import ConfiguredSecurityBuilder
from guniflask.web.request_filter import RequestFilter

__all__ = ['WebSecurity']


class WebSecurity(ConfiguredSecurityBuilder):
    def __init__(self):
        super().__init__()
        self._request_filters: Dict[TypeVar[RequestFilter], RequestFilter] = {}
        self._security_builders: List[SecurityBuilder] = []

    def _perform_build(self):
        for t, f in self._request_filters.items():
            d = set(t.__dict__.keys())
            if 'before_request' in d:
                current_app.before_request(f.before_request)
            if 'after_request' in d:
                current_app.after_request(f.after_request)
        for builder in self._security_builders:
            builder.build()

    def add_security_builder(self, security_builder: SecurityBuilder):
        self._security_builders.append(security_builder)

    def add_request_filter(self, request_filter: RequestFilter):
        self._request_filters[type(request_filter)] = request_filter
