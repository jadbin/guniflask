# coding=utf-8

from guniflask.context.annotation import configuration, bean
from guniflask.oauth2.client_details import ClientDetails
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
        return ClientDetailsServiceDelegator(self._configurer)


class ClientDetailsServiceDelegator(ClientDetailsService):
    def __init__(self, delegate_builder: ClientDetailsServiceConfigurer):
        self._delegate_builder = delegate_builder
        self._delegate: ClientDetailsService = None

    def load_client_details_by_client_id(self, client_id) -> ClientDetails:
        if self._delegate is None:
            self._delegate = self._delegate_builder.client_details_service
            self._delegate_builder = None
        return self._delegate.load_client_details_by_client_id(client_id)
