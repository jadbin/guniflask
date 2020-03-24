# coding=utf-8

from guniflask.beans.factory_hook import InitializingBean
from guniflask.oauth2.token_granter import TokenGranter
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.request_factory import OAuth2RequestFactory, DefaultOAuth2RequestFactory

__all__ = ['AbstractEndpoint']


class AbstractEndpoint(InitializingBean):
    def __init__(self, token_granter: TokenGranter, client_details_service: ClientDetailsService):
        self.token_granter = token_granter
        self.client_details_service = client_details_service
        self.oauth2_request_factory: OAuth2RequestFactory = None

    def after_properties_set(self):
        assert self.token_granter is not None, 'Token granter is required'
        assert self.client_details_service is not None, 'Client details service is required'
        if self.oauth2_request_factory is None:
            self.oauth2_request_factory = DefaultOAuth2RequestFactory(self.client_details_service)
