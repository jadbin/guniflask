# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.oauth2_config.resource_server_builder import ResourceServerSecurityConfigurer
from guniflask.security_config.http_security import HttpSecurity

__all__ = ['ResourceServerConfigurer', 'ResourceServerConfigurerAdapter']


class ResourceServerConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def configure_security(self, resources: ResourceServerSecurityConfigurer):
        pass

    @abstractmethod
    def configure_http(self, http: HttpSecurity):
        pass


class ResourceServerConfigurerAdapter(ResourceServerConfigurer):
    def configure_security(self, resources: ResourceServerSecurityConfigurer):
        pass

    def configure_http(self, http: HttpSecurity):
        pass
