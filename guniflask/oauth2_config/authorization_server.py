# coding=utf-8

from guniflask.oauth2_config.authorization_server_endpoints_configurer import AuthorizationServerEndpointsConfigurer
from guniflask.oauth2_config.client_details_service_configurer import ClientDetailsServiceConfigurer

__all__ = ['AuthorizationServerConfigurer']


class AuthorizationServerConfigurer:
    def configure_endpoints(self, endpoints: AuthorizationServerEndpointsConfigurer):
        pass

    def configure_client_details_service(self, clients: ClientDetailsServiceConfigurer):
        pass
