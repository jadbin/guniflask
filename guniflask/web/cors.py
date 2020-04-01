# coding=utf-8

from flask_cors.core import get_cors_options, parse_resources
from flask_cors.extension import make_after_request_function

from guniflask.web.request_filter import RequestFilter

__all__ = ['CorsFilter']


class CorsFilter(RequestFilter):
    DEFAULT_CONFIG = dict(origins='*',
                          methods=['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE'],
                          allow_headers='*',
                          expose_headers=None,
                          supports_credentials=False,
                          max_age=None)

    def __init__(self, resources=None, **kwargs):
        self.default_config = dict(self.DEFAULT_CONFIG)
        self.resources = {}
        self._after_request = None

        self._set_default_config(**kwargs)
        if resources and isinstance(resources, dict):
            for k, v in resources.items():
                if isinstance(v, dict):
                    self._add_resource(k, **v)
                else:
                    self._add_resource(k)
        self._init()

    def _set_default_config(self, **kwargs):
        for k in self.default_config:
            if k in kwargs:
                self.default_config[k] = kwargs[k]

    def _add_resource(self, pattern, **kwargs):
        self.resources[pattern] = dict(self.DEFAULT_CONFIG)
        for k in self.DEFAULT_CONFIG:
            if k in kwargs:
                self.resources[pattern][k] = kwargs[k]

    def _init(self):
        # fake app
        app = object()
        kwargs = dict(self.default_config)
        if self.resources:
            kwargs['resources'] = self.resources

        options = get_cors_options(app, kwargs)
        resources = parse_resources(options.get('resources'))
        resources = [
            (pattern, get_cors_options(app, options, opts))
            for (pattern, opts) in resources
        ]
        self._after_request = make_after_request_function(resources)

    def after_request(self, response):
        return self._after_request(response)
