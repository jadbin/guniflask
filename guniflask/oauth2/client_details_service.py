# coding=utf-8

from guniflask.oauth2.client_details import ClientDetails

__all__ = ['ClientDetailsService']


class ClientDetailsService:
    """
    A service that provides the details about an OAuth2 client.
    """

    def __init__(self):
        self._client_details_store = {}

    def load_client_details_by_client_id(self, client_id) -> ClientDetails:
        return self._client_details_store.get(client_id)

    def add_client_details(self, client_details):
        self._client_details_store[client_details.client_id] = client_details

    def remove_client_details(self, client_details):
        client_id = client_details.client_id
        if client_id in self._client_details_store:
            self._client_details_store.pop(client_id)
