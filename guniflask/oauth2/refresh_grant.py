# coding=utf-8

from guniflask.oauth2.token_granter import AbstractTokenGranter
from guniflask.oauth2.token_service import AuthorizationServerTokenServices
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.request_factory import OAuth2RequestFactory
from guniflask.oauth2.request import TokenRequest
from guniflask.oauth2.token import OAuth2AccessToken
from guniflask.oauth2.client_details import ClientDetails

__all__ = ['RefreshTokenGranter']


class RefreshTokenGranter(AbstractTokenGranter):
    GRANT_TYPE = 'refresh_token'

    def __init__(self, token_services: AuthorizationServerTokenServices,
                 client_details_service: ClientDetailsService,
                 request_factory: OAuth2RequestFactory):
        super().__init__(token_services, client_details_service, request_factory, self.GRANT_TYPE)

    def _get_access_token(self, token_request: TokenRequest, client: ClientDetails) -> OAuth2AccessToken:
        refresh_token_value = token_request.request_parameters.get('refresh_token')
        return self.token_services.refresh_access_token(refresh_token_value, token_request)
