# coding=utf-8

__all__ = ['ClientDetails', 'ClientDetailsService']


class ClientDetails:
    """
    Client details for OAuth2
    """

    def __init__(self, client_id=None, client_secret=None, resources_ids=None, scopes=None, grant_types=None,
                 authorities=None, redirect_uris=None, auto_approve_scopes=None,
                 access_token_expires_in=None, refresh_token_expires_in=None,
                 additional_information=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource_ids = set()
        if resources_ids is not None:
            self.resource_ids.update(resources_ids)
        self.scopes = set()
        if scopes is not None:
            self.scopes.update(scopes)
        self.grant_types = set()
        if grant_types is not None:
            self.grant_types.update(grant_types)
        self.authorities = set()
        if authorities is not None:
            self.authorities.update(authorities)
        self.redirect_uris = set()
        if redirect_uris is not None:
            self.redirect_uris.update(redirect_uris)
        self.auto_approve_scopes = set()
        if auto_approve_scopes is not None:
            self.auto_approve_scopes.update(auto_approve_scopes)
        self.access_token_expires_in = access_token_expires_in
        self.refresh_token_expires_in = refresh_token_expires_in
        self.additional_information = {}
        if additional_information is not None:
            self.additional_information.update(additional_information)

    def is_scoped(self):
        return self.scopes is not None and len(self.scopes) > 0

    def is_auto_approve(self, scope):
        return self.auto_approve_scopes is not None and scope in self.auto_approve_scopes


class ClientDetailsService:
    """
    A service that provides the details about an OAuth2 client.
    """

    def __init__(self):
        self._client_details_store = {}

    def load_client_details_by_client_id(self, client_id):
        return self._client_details_store.get(client_id)

    def add_client_details(self, client_details):
        self._client_details_store[client_details.client_id] = client_details

    def remove_client_details(self, client_details):
        client_id = client_details.client_id
        if client_id in self._client_details_store:
            self._client_details_store.pop(client_id)
