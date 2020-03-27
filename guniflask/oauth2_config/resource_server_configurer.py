# coding=utf-8

from guniflask.oauth2_config.resource_server_security_configurer import ResourceServerSecurityConfigurer

__all__ = ['ResourceServerConfigurer']


class ResourceServerConfigurer:
    def configure(self, resources: ResourceServerSecurityConfigurer):
        pass
