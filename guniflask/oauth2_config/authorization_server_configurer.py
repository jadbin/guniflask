# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.oauth2_config.authorization_server_builder import AuthorizationServerEndpointsConfigurer, \
    AuthorizationServerSecurityConfigurer
from guniflask.oauth2_config.client_details_service_configurer import ClientDetailsServiceConfigurer

__all__ = ['AuthorizationServerConfigurer', 'AuthorizationServerConfigurerAdapter']


class AuthorizationServerConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def configure_endpoints(self, endpoints: AuthorizationServerEndpointsConfigurer):
        pass

    @abstractmethod
    def configure_client_details_service(self, clients: ClientDetailsServiceConfigurer):
        pass

    @abstractmethod
    def configure_security(self, security: AuthorizationServerSecurityConfigurer):
        pass


class AuthorizationServerConfigurerAdapter(AuthorizationServerConfigurer):
    def configure_endpoints(self, endpoints: AuthorizationServerEndpointsConfigurer):
        pass

    def configure_client_details_service(self, clients: ClientDetailsServiceConfigurer):
        pass

    def configure_security(self, security: AuthorizationServerSecurityConfigurer):
        pass
