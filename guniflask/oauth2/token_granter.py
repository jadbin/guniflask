# coding=utf-8

from abc import ABCMeta, abstractmethod
from typing import Optional, Collection

from guniflask.oauth2.token_service import AuthorizationServerTokenServices
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.request_factory import OAuth2RequestFactory
from guniflask.oauth2.request import TokenRequest
from guniflask.oauth2.token import OAuth2AccessToken
from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.client_details import ClientDetails
from guniflask.oauth2.errors import InvalidClientError

__all__ = ['TokenGranter', 'AbstractTokenGranter', 'CompositeTokenGranter']


class TokenGranter(metaclass=ABCMeta):

    @abstractmethod
    def grant(self, grant_type: str, token_request: TokenRequest) -> Optional[OAuth2AccessToken]:
        pass


class AbstractTokenGranter(TokenGranter):
    def __init__(self, token_services: AuthorizationServerTokenServices, client_details_service: ClientDetailsService,
                 request_factory: OAuth2RequestFactory, grant_type: str):
        self.token_services = token_services
        self.client_details_service = client_details_service
        self.request_factory = request_factory
        self.grant_type = grant_type

    def grant(self, grant_type, token_request):
        if grant_type != self.grant_type:
            return
        client_id = token_request.client_id
        client = self.client_details_service.load_client_details_by_client_id(client_id)
        self._validate_grant_type(grant_type, client)
        return self._get_access_token(token_request, client)

    def _get_access_token(self, token_request: TokenRequest, client: ClientDetails) -> OAuth2AccessToken:
        return self.token_services.create_access_token(self._get_oauth2_authentication(token_request, client))

    def _get_oauth2_authentication(self, token_request: TokenRequest,
                                   client: ClientDetails) -> OAuth2Authentication:
        oauth2_request = self.request_factory.create_oauth2_request_from_token_request(token_request, client)
        return OAuth2Authentication(oauth2_request)

    def _validate_grant_type(self, grant_type: str, client_details: ClientDetails):
        authorized_grant_types = client_details.grant_types
        if authorized_grant_types and grant_type not in authorized_grant_types:
            raise InvalidClientError('Unauthorized grant type: {}'.format(grant_type))


class CompositeTokenGranter(TokenGranter):
    def __init__(self, token_granters: Collection[TokenGranter] = None):
        self.token_granters = [] if token_granters is None else list(token_granters)

    def grant(self, grant_type: str, token_request: TokenRequest) -> Optional[OAuth2AccessToken]:
        for granter in self.token_granters:
            result = granter.grant(grant_type, token_request)
            if result is not None:
                return result

    def add_token_granter(self, token_granter):
        self.token_granters.append(token_granter)
