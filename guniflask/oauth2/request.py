# coding=utf-8

from guniflask.oauth2.client_details import ClientDetails
from guniflask.oauth2.oauth2_utils import OAuth2Utils

__all__ = ['AuthorizationRequest', 'TokenRequest', 'OAuth2Request']


class BaseRequest:
    def __init__(self, client_id: str = None, scope: set = None, request_parameters: dict = None):
        self.client_id = client_id
        self.scope = set()
        if scope is not None:
            self.scope.update(scope)
        self.request_parameters = {}
        if request_parameters is not None:
            self.request_parameters.update(request_parameters)


class AuthorizationRequest(BaseRequest):
    def __init__(self, approval_parameters: dict = None, authorities: set = None, approved: bool = None,
                 resource_ids: set = None, redirect_uri: str = None, response_types: set = None, state: str = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.approval_parameters = {}
        if approval_parameters is not None:
            self.approval_parameters.update(approval_parameters)
        self.resource_ids = set()
        self.authorities = set()
        if authorities is not None:
            self.authorities.update(authorities)
        self.approved = False
        if approved is not None:
            self.approved = approved
        self.resource_ids = {}
        if resource_ids is not None:
            self.resource_ids = {}
        if resource_ids is not None:
            self.resource_ids.update(resource_ids)
        self.redirect_uri = redirect_uri
        self.response_types = set()
        if response_types is not None:
            self.response_types.update(response_types)
        self.state = state

    def set_from_client_details(self, client_details: ClientDetails):
        self.resource_ids = client_details.resource_ids
        self.authorities = client_details.authorities


class TokenRequest(BaseRequest):
    def __init__(self, grant_type: str = None, **kwargs):
        self.grant_type = grant_type
        super().__init__(**kwargs)


class OAuth2Request(BaseRequest):
    def __init__(self, authorities: set = None, approved: bool = None, resource_ids: set = None,
                 redirect_uri: str = None, response_types: set = None, **kwargs):
        super().__init__(**kwargs)
        self.authorities = set()
        if authorities is not None:
            self.authorities.update(authorities)
        self.approved = False
        if approved is not None:
            self.approved = approved
        self.resource_ids = {}
        if resource_ids is not None:
            self.resource_ids.update(resource_ids)
        self.redirect_uri = redirect_uri
        self.response_types = set()
        if response_types is not None:
            self.response_types.update(response_types)
        self.refresh: TokenRequest = None

    @property
    def grant_type(self):
        if OAuth2Utils.GRANT_TYPE in self.request_parameters:
            return self.request_parameters[OAuth2Utils.GRANT_TYPE]
        if OAuth2Utils.RESPONSE_TYPE in self.request_parameters:
            response = self.request_parameters[OAuth2Utils.RESPONSE_TYPE]
            if 'token' in response:
                return 'implicit'

    def copy(self):
        request = self.__class__(request_parameters=self.request_parameters,
                                 client_id=self.client_id,
                                 scope=self.scope,
                                 authorities=self.authorities,
                                 approved=self.approved,
                                 resource_ids=self.resource_ids,
                                 redirect_uri=self.redirect_uri,
                                 response_types=self.response_types)
        request.refresh = self.refresh
        return request

    def do_refresh(self, token_request: TokenRequest):
        request = self.copy()
        request.refresh = token_request
        return request

    def narrow_scope(self, scope: set):
        request = self.copy()
        request.scope = scope
        return request
