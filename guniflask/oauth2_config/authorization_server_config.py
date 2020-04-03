# coding=utf-8

from typing import List

from guniflask.context.annotation import configuration, bean, include
from guniflask.beans.annotation import autowired
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.token_converter import JwtAccessTokenConverter
from guniflask.oauth2.token_endpoint import TokenKeyEndpoint, TokenEndpoint
from guniflask.oauth2_config.client_details_service_configurer import ClientDetailsServiceConfigurer
from guniflask.oauth2_config.client_details_service_config import ClientDetailsServiceConfiguration
from guniflask.oauth2_config.authorization_server_configurer import AuthorizationServerConfigurer, \
    AuthorizationServerEndpointsConfigurer, AuthorizationServerSecurityConfigurer
from guniflask.security_config.web_security_configurer import WebSecurityConfigurer
from guniflask.security_config.authentication_manager_builder import AuthenticationManagerBuilder
from guniflask.security_config.http_security import HttpSecurity

__all__ = ['AuthorizationServerEndpointsConfiguration',
           'AuthorizationServerSecurityConfiguration']


@configuration
class AuthorizationServerEndpointsConfiguration:
    def __init__(self, client_details_service: ClientDetailsService,
                 configurers: List[AuthorizationServerConfigurer] = None):
        self._client_details_service = client_details_service
        self._endpoints = AuthorizationServerEndpointsConfigurer()
        self._endpoints.with_client_details_service(client_details_service)
        if configurers:
            for c in configurers:
                c.configure_endpoints(self._endpoints)

    @property
    def endpoints_configurer(self):
        return self._endpoints

    @bean
    def token_endpoint(self) -> TokenEndpoint:
        token_endpoint = TokenEndpoint(self._endpoints.token_granter, self._client_details_service)
        token_endpoint.oauth2_request_factory = self._endpoints.oauth2_request_factory
        token_endpoint.oauth2_request_validator = self._endpoints.oauth2_request_validator
        return token_endpoint

    @bean
    def token_key_endpoint(self) -> TokenKeyEndpoint:
        access_token_converter = self._endpoints.access_token_converter
        if isinstance(access_token_converter, JwtAccessTokenConverter):
            token_key_endpoint = TokenKeyEndpoint(access_token_converter)
            return token_key_endpoint


@configuration
@include(ClientDetailsServiceConfiguration, AuthorizationServerEndpointsConfiguration)
class AuthorizationServerSecurityConfiguration(WebSecurityConfigurer):
    def __init__(self, client_details_service: ClientDetailsService,
                 endpoints: AuthorizationServerEndpointsConfiguration,
                 configurers: List[AuthorizationServerConfigurer] = None):
        super().__init__()
        self._client_details_service = client_details_service
        self._endpoints = endpoints
        self._configurers = configurers

    @autowired
    def configure_client_details_service(self, client_details: ClientDetailsServiceConfigurer):
        if self._configurers:
            for c in self._configurers:
                c.configure_client_details_service(client_details)

    def configure_http(self, http: HttpSecurity):
        configurer = AuthorizationServerSecurityConfigurer()
        self._configure_security(configurer)
        http.apply(configurer)

        http \
            .authorize_blueprint(TokenEndpoint) \
            .authorize_blueprint(TokenKeyEndpoint) \
            .http_basic()

        http.set_shared_object(ClientDetailsService, self._client_details_service)

    def configure_authentication(self, authentication_builder: AuthenticationManagerBuilder):
        self._enable_local_authentication = True

    def _configure_security(self, configurer: AuthorizationServerSecurityConfigurer):
        if self._configurers:
            for c in self._configurers:
                c.configure_security(configurer)
