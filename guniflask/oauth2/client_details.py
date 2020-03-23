# coding=utf-8

__all__ = ['ClientDetails']


class ClientDetails:
    """
    Client details for OAuth2
    """

    def __init__(self, client_id=None, client_secret=None, resources_ids=None, scope=None, grant_types=None,
                 authorities=None, redirect_uris=None, auto_approve_scopes=None,
                 access_token_expires_in=None, refresh_token_expires_in=None,
                 additional_information=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource_ids = set()
        if resources_ids is not None:
            self.resource_ids.update(resources_ids)
        self.scope = set()
        if scope is not None:
            self.scope.update(scope)
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
        return self.scope is not None and len(self.scope) > 0

    def is_auto_approve(self, scope):
        return self.auto_approve_scopes is not None and scope in self.auto_approve_scopes
