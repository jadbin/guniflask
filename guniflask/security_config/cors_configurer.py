# coding=utf-8

from guniflask.security_config.http_security_builder import HttpSecurityBuilder
from guniflask.security_config.security_configurer import SecurityConfigurerAdapter
from guniflask.web.cors import CorsFilter

__all__ = ['CorsConfigurer']


class CorsConfigurer(SecurityConfigurerAdapter):

    def __init__(self, cors=None):
        super().__init__()

        self.cors_filter = CorsFilter()
        if isinstance(cors, dict):
            self.cors_filter.set_default_config(**cors)
            resources = cors.get('resources')
            if resources and isinstance(resources, dict):
                for k, v in resources.items():
                    if isinstance(v, dict):
                        self.cors_filter.add_resource(k, **v)
                    else:
                        self.cors_filter.add_resource(k)

    def configure(self, http: HttpSecurityBuilder):
        self.cors_filter.configure()
