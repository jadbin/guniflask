# coding=utf-8

from guniflask.context.annotation import configuration, bean
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2_config.client_details_service_configurer import ClientDetailsServiceConfigurer

__all__ = ['ClientDetailsServiceConfiguration']


@configuration
class ClientDetailsServiceConfiguration:
    def __init__(self):
        self._configurer = ClientDetailsServiceConfigurer()

    @bean
    def client_details_configurer(self) -> ClientDetailsServiceConfigurer:
        return self._configurer

    @bean
    def client_details_service(self) -> ClientDetailsService:
        return self._configurer.client_details_service
