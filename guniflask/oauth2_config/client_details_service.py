# coding=utf-8

from guniflask.context.annotation import configuration, bean
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2_config.authorization_server import AuthorizationServerConfigurer
from guniflask.oauth2_config.client_details_service_configurer import ClientDetailsServiceConfigurer

__all__ = ['ClientDetailsServiceConfiguration']


@configuration
class ClientDetailsServiceConfiguration:
    def __init__(self, authorization_server_configurer: AuthorizationServerConfigurer):
        self.service = ClientDetailsServiceConfigurer()
        authorization_server_configurer.configure_client_details_service(self.service)

    @bean
    def client_details_service(self) -> ClientDetailsService:
        return self.service.get_client_details_service()
