# coding=utf-8

from guniflask.oauth2.token_granter import AbstractTokenGranter
from guniflask.oauth2.token_service import AuthorizationServerTokenServices
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.request_factory import OAuth2RequestFactory

__all__ = ['ClientCredentialsTokenGranter']


class ClientCredentialsTokenGranter(AbstractTokenGranter):
    GRANT_TYPE = 'client_credentials'

    def __init__(self, token_services: AuthorizationServerTokenServices, client_details_service: ClientDetailsService,
                 request_factory: OAuth2RequestFactory):
        super().__init__(token_services, client_details_service, request_factory, self.GRANT_TYPE)
        self.allow_refresh = False

    def grant(self, grant_type, token_request):
        token = super().grant(grant_type, token_request)
        if token and not self.allow_refresh:
            token = token.copy()
            token.refresh_token = None
        return token
