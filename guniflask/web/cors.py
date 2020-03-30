# coding=utf-8

from flask import current_app
from flask_cors import CORS

__all__ = ['CorsFilter']


class CorsFilter:
    DEFAULT_CONFIG = dict(origins='*',
                          methods=['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE'],
                          allow_headers='*',
                          expose_headers=None,
                          supports_credentials=False,
                          max_age=None)

    def __init__(self):
        self.default_config = dict(self.DEFAULT_CONFIG)
        self.resources = {}

    def set_default_config(self, **kwargs):
        for k in self.default_config:
            if k in kwargs:
                self.default_config[k] = kwargs[k]

    def add_resource(self, pattern, **kwargs):
        self.resources[pattern] = dict(self.DEFAULT_CONFIG)
        for k in self.DEFAULT_CONFIG:
            if k in kwargs:
                self.resources[pattern][k] = kwargs[k]

    def configure(self):
        cors = CORS()
        kwargs = dict(self.default_config)
        if self.resources:
            kwargs['resources'] = self.resources
        app = current_app._get_current_object()
        cors.init_app(app, **kwargs)
