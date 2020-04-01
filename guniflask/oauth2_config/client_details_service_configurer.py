# coding=utf-8

from guniflask.oauth2.client_details_service import ClientDetailsService

__all__ = ['ClientDetailsServiceConfigurer']


class ClientDetailsServiceConfigurer:
    def __init__(self):
        self._client_details_service: ClientDetailsService = None

    @property
    def client_details_service(self) -> ClientDetailsService:
        return self._client_details_service

    def with_client_details_service(self, client_details_service: ClientDetailsService
                                    ) -> 'ClientDetailsServiceConfigurer':
        self._client_details_service = client_details_service
        return self
