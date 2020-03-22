# coding=utf-8

from flask_cors import CORS

from guniflask.config.utils import map_dict_config


class CorsManager:
    class CorsConfig:
        origins = '*'
        methods = ['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE']
        allow_headers = '*'
        expose_headers = None
        supports_credentials = False
        max_age = None

        def to_dict(self):
            return {
                'origins': self.origins,
                'methods': self.methods,
                'allow_headers': self.allow_headers,
                'expose_headers': self.expose_headers,
                'supports_credentials': self.supports_credentials,
                'max_age': self.max_age
            }

    def __init__(self):
        self.config = self.CorsConfig()
        self.resources = None
        self._cors = CORS()

    @classmethod
    def from_config(cls, config: dict):
        obj = cls()
        map_dict_config(config, obj.config)
        if 'resources' in config:
            obj.resources = config['resources']
            if isinstance(obj.resources, dict):
                for k in obj.resources:
                    v = obj.resources[k]
                    if isinstance(v, dict):
                        c = cls.CorsConfig()
                        map_dict_config(v, c)
                        obj.resources[k] = c
        return obj

    def init_app(self, app):
        kwargs = self.config.to_dict()
        if self.resources:
            if isinstance(self.resources, dict):
                r = {}
                for k, v in self.resources.items():
                    if isinstance(v, self.CorsConfig):
                        r[k] = v.to_dict()
                    else:
                        r[k] = v
            else:
                r = self.resources
            kwargs['resources'] = r
        self._cors.init_app(app, **kwargs)
