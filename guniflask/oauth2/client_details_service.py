# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.oauth2.client_details import ClientDetails
from guniflask.oauth2.errors import NoSuchClientError

__all__ = ['ClientDetailsService', 'InMemoryClientDetailsService']


class ClientDetailsService(metaclass=ABCMeta):
    """
    A service that provides the details about an OAuth2 client.
    """

    @abstractmethod
    def load_client_details_by_client_id(self, client_id) -> ClientDetails:
        pass


class InMemoryClientDetailsService(ClientDetailsService):
    def __init__(self, client_details_store: dict = None):
        self.client_details_store = {}
        if client_details_store:
            self.client_details_store.update(client_details_store)

    def load_client_details_by_client_id(self, client_id: str) -> ClientDetails:
        if client_id not in self.client_details_store:
            raise NoSuchClientError('No client found with id = {}'.format(client_id))
        return self.client_details_store[client_id]
