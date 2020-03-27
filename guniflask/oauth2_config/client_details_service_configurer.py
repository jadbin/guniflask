# coding=utf-8

from guniflask.oauth2.client_details_service import ClientDetailsService

__all__ = ['ClientDetailsServiceConfigurer']


class ClientDetailsServiceConfigurer:
    def __init__(self):
        self.client_details_service: ClientDetailsService = None

    def get_client_details_service(self):
        return self.client_details_service
