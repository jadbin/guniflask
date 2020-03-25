# coding=utf-8

from typing import Collection

from guniflask.context.annotation import configuration
from guniflask.oauth2_config.authorization_server import AuthorizationServerConfigurer
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.token_service import AuthorizationServerTokenServices, DefaultTokenServices
from guniflask.oauth2.token_store import TokenStore, JwtTokenStore
from guniflask.oauth2.token_converter import TokenEnhancer, AccessTokenConverter, JwtAccessTokenConverter
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.oauth2.request_factory import OAuth2RequestFactory, OAuth2RequestValidator, \
    DefaultOAuth2RequestValidator, DefaultOAuth2RequestFactory
from guniflask.oauth2.token_granter import TokenGranter, CompositeTokenGranter
from guniflask.oauth2.password_grant import PasswordTokenGranter
from guniflask.oauth2.client_grant import ClientCredentialsTokenGranter
from guniflask.oauth2.refresh_grant import RefreshTokenGranter

__all__ = ['AuthorizationServerEndpointsConfigurer', 'AuthorizationServerEndpointsConfiguration']


class AuthorizationServerEndpointsConfigurer:
    def __init__(self, client_details_service: ClientDetailsService):
        self._client_details_service = client_details_service
        self.token_services: AuthorizationServerTokenServices = None
        self.token_store: TokenStore = None
        self.token_enhancer: TokenEnhancer = None
        self.access_token_converter: AccessTokenConverter = None
        self.token_granter: TokenGranter = None
        self.request_factory: OAuth2RequestFactory = None
        self.request_validator: OAuth2RequestValidator = None
        self.authentication_manager: AuthenticationManager = None

    def get_token_services(self) -> AuthorizationServerTokenServices:
        if self.token_services is None:
            self.token_services = self._create_default_token_services()
        return self.token_services

    def get_token_store(self) -> TokenStore:
        if self.token_store is None:
            access_token_converter = self.get_access_token_converter()
            if isinstance(access_token_converter, JwtAccessTokenConverter):
                self.token_store = JwtTokenStore(access_token_converter)
        return self.token_store

    def get_token_enhancer(self) -> TokenEnhancer:
        if self.token_enhancer is None:
            access_token_converter = self.get_access_token_converter()
            if isinstance(access_token_converter, JwtAccessTokenConverter):
                self.token_enhancer = access_token_converter
        return self.token_enhancer

    def get_access_token_converter(self) -> AccessTokenConverter:
        if self.access_token_converter is None:
            self.access_token_converter = JwtAccessTokenConverter()
        return self.access_token_converter

    def get_token_granter(self) -> TokenGranter:
        if self.token_granter is None:
            self.token_granter = CompositeTokenGranter(self._get_default_token_granters())
        return self.token_granter

    def get_request_factory(self) -> OAuth2RequestFactory:
        if self.request_factory is None:
            self.request_factory = DefaultOAuth2RequestFactory(self._client_details_service)
        return self.request_factory

    def get_request_validator(self) -> OAuth2RequestValidator:
        if self.request_validator is None:
            self.request_validator = DefaultOAuth2RequestValidator()
        return self.request_validator

    def get_authentication_manager(self) -> AuthenticationManager:
        return self.authentication_manager

    def _create_default_token_services(self) -> AuthorizationServerTokenServices:
        token_services = DefaultTokenServices(self.get_token_store())
        token_services.support_refresh_token = True
        token_services.token_enhancer = self.get_token_enhancer()
        token_services.client_details_service = self._client_details_service
        return token_services

    def _get_default_token_granters(self) -> Collection[TokenGranter]:
        token_granters = []
        token_services = self.get_token_services()
        request_factory = self.get_request_factory()
        token_granters.append(RefreshTokenGranter(token_services, self._client_details_service, request_factory))
        token_granters.append(ClientCredentialsTokenGranter(token_services,
                                                            self._client_details_service,
                                                            request_factory))
        authentication_manager = self.get_authentication_manager()
        if authentication_manager is not None:
            token_granters.append(PasswordTokenGranter(authentication_manager,
                                                       token_services,
                                                       self._client_details_service,
                                                       request_factory))
        return token_granters


@configuration
class AuthorizationServerEndpointsConfiguration:
    def __init__(self, authorization_server_configurer: AuthorizationServerConfigurer,
                 client_details_service: ClientDetailsService):
        self.endpoints = AuthorizationServerEndpointsConfigurer(client_details_service)
        authorization_server_configurer.configure_endpoints(self.endpoints)
