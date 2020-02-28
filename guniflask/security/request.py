# coding=utf-8

__all__ = ['OAuth2Request', 'OAuth2RequestFactory']


class BaseRequest:
    def __init__(self, client_id=None, scope=None, request_parameters=None):
        self._client_id = client_id
        self._scope = set()
        if scope is not None:
            self._scope.update(scope)
        self._request_parameters = {}
        if request_parameters is not None:
            self._request_parameters.update(request_parameters)

    @property
    def client_id(self):
        return self._client_id

    @property
    def scope(self):
        return self._scope

    @property
    def request_parameters(self):
        return self._request_parameters


class OAuth2Request(BaseRequest):
    def __init__(self, authorities=None, approved=None, resource_ids=None, redirect_uri=None, response_types=None,
                 **kwargs):
        super().__init__(**kwargs)
        self._authorities = set()
        if authorities is not None:
            self._authorities.update(authorities)
        self._approved = False
        if approved is not None:
            self._approved = approved
        self._resource_ids = {}
        if resource_ids is not None:
            self._resource_ids.update(resource_ids)
        self._redirect_uri = redirect_uri
        self._response_types = set()
        if response_types is not None:
            self._response_types.update(response_types)
        self._refresh = None

    @property
    def is_approved(self):
        return self._approved

    @property
    def authorities(self):
        return self._authorities

    @property
    def resource_ids(self):
        return self._resource_ids

    @property
    def redirect_uri(self):
        return self._redirect_uri

    @property
    def response_types(self):
        return self._response_types


class OAuth2RequestFactory:
    """
    Strategy for managing OAuth2 requests
    """


