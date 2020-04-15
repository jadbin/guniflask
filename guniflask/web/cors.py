# coding=utf-8

from flask_cors.core import parse_resources, serialize_options, DEFAULT_OPTIONS
from flask_cors.extension import make_after_request_function

from guniflask.web.request_filter import RequestFilter

__all__ = ['CorsFilter']


class CorsFilter(RequestFilter):

    def __init__(self, **kwargs):
        options = self._get_cors_options(kwargs)
        resources = parse_resources(options.get('resources'))
        resources = [
            (pattern, self._get_cors_options(options, opts))
            for (pattern, opts) in resources
        ]
        self._after_request = make_after_request_function(resources)

    def _get_cors_options(self, *dicts):
        options = dict(DEFAULT_OPTIONS)
        for d in dicts:
            options.update(d)
        return serialize_options(options)

    def after_request(self, response):
        return self._after_request(response)
