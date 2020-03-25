# coding=utf-8

from abc import ABCMeta, abstractmethod
from typing import Union

from guniflask.oauth2.client_details import ClientDetails
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.oauth2_utils import OAuth2Utils
from guniflask.oauth2.request import AuthorizationRequest, OAuth2Request, TokenRequest
from guniflask.oauth2.errors import InvalidClientError, InvalidScopeError

__all__ = ['OAuth2RequestFactory', 'DefaultOAuth2RequestFactory',
           'OAuth2RequestValidator', 'DefaultOAuth2RequestValidator']


class OAuth2RequestFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_authorization_request(self, authorization_parameters: dict) -> AuthorizationRequest:
        pass

    @abstractmethod
    def create_oauth2_request_from_authorization_request(self, request: AuthorizationRequest) -> OAuth2Request:
        pass

    @abstractmethod
    def create_oauth2_request_from_token_request(self, request: TokenRequest,
                                                 client_details: ClientDetails) -> OAuth2Request:
        pass

    @abstractmethod
    def create_token_request(self, request_parameters: dict, authenticated_client: ClientDetails) -> TokenRequest:
        pass

    @abstractmethod
    def create_token_request_from_authorization_request(self, request: AuthorizationRequest,
                                                        grant_type: str) -> TokenRequest:
        pass


class DefaultOAuth2RequestFactory(OAuth2RequestFactory):
    """
    Strategy for managing OAuth2 requests
    """

    def __init__(self, client_details_service: ClientDetailsService):
        self.client_details_service = client_details_service

    def create_authorization_request(self, authorization_parameters: dict):
        client_id = authorization_parameters.get(OAuth2Utils.CLIENT_ID)
        state = authorization_parameters.get(OAuth2Utils.STATE)
        redirect_uri = authorization_parameters.get(OAuth2Utils.REDIRECT_URI)
        response_types = OAuth2Utils.parse_parameter_list(authorization_parameters.get(OAuth2Utils.RESPONSE_TYPE))
        scopes = self._extract_scopes(authorization_parameters, client_id)
        request = AuthorizationRequest(request_parameters=authorization_parameters,
                                       client_id=client_id,
                                       scope=scopes,
                                       approved=False,
                                       state=state,
                                       redirect_uri=redirect_uri,
                                       response_types=response_types)
        client_details = self.client_details_service.load_client_details_by_client_id(client_id)
        request.set_from_client_details(client_details)
        return request

    def create_oauth2_request_from_authorization_request(self, request: AuthorizationRequest):
        oauth2_request = OAuth2Request(request_parameters=request.request_parameters,
                                       client_id=request.client_id,
                                       scope=request.scope,
                                       authorities=request.authorities,
                                       approved=request.approved,
                                       resource_ids=request.resource_ids,
                                       redirect_uri=request.redirect_uri,
                                       response_types=request.response_types)
        return oauth2_request

    def create_token_request(self, request_parameters: dict, authenticated_client: ClientDetails):
        client_id = request_parameters.get(OAuth2Utils.CLIENT_ID)
        if client_id is None:
            client_id = authenticated_client.client_id
        else:
            if client_id != authenticated_client.client_id:
                raise InvalidClientError('Given client ID does not match authenticated client')
        grant_type = request_parameters.get(OAuth2Utils.GRANT_TYPE)
        scopes = self._extract_scopes(request_parameters, client_id)
        request = TokenRequest(request_parameters=request_parameters,
                               client_id=client_id,
                               scope=scopes,
                               grant_type=grant_type)
        return request

    def create_token_request_from_authorization_request(self, request: AuthorizationRequest, grant_type: str):
        token_request = TokenRequest(request_parameters=request.request_parameters,
                                     client_id=request.client_id,
                                     scope=request.scope,
                                     grant_type=grant_type)
        return token_request

    def create_oauth2_request_from_token_request(self, request: TokenRequest, client_details: ClientDetails):
        request_parameters = dict(request.request_parameters)
        if 'password' in request_parameters:
            request_parameters.pop('password')
        if 'client_secret' in request_parameters:
            request_parameters.pop('client_secret')
        request_parameters['grant_type'] = request.grant_type
        oauth2_request = OAuth2Request(request_parameters=request_parameters,
                                       client_id=client_details.client_id,
                                       scope=request.scope,
                                       authorities=client_details.authorities,
                                       approved=True,
                                       resource_ids=client_details.resource_ids)
        return oauth2_request

    def _extract_scopes(self, request_parameters: dict, client_id: str):
        scopes = OAuth2Utils.parse_parameter_list(request_parameters.get(OAuth2Utils.SCOPE))
        client_details = self.client_details_service.load_client_details_by_client_id(client_id)
        if not scopes:
            scopes = client_details.scope
        return scopes


class OAuth2RequestValidator(metaclass=ABCMeta):
    @abstractmethod
    def validate_scope(self, request: Union[AuthorizationRequest, TokenRequest], client: ClientDetails):
        pass


class DefaultOAuth2RequestValidator(OAuth2RequestValidator):
    def validate_scope(self, request: Union[AuthorizationRequest, TokenRequest], client: ClientDetails):
        self._validate_request_scope(request.scope, client.scope)

    def _validate_request_scope(self, request_scopes: set, client_scopes: set):
        if client_scopes:
            for scope in request_scopes:
                if scope not in client_scopes:
                    raise InvalidScopeError('Invalid scope: {}'.format(scope))
