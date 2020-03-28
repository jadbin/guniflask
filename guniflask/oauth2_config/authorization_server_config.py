# coding=utf-8

from guniflask.context.annotation import configuration, bean
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.token_converter import JwtAccessTokenConverter
from guniflask.oauth2.token_endpoint import TokenKeyEndpoint, TokenEndpoint
from guniflask.oauth2_config.authorization_server_configurer import AuthorizationServerEndpointsConfigurer, \
    AuthorizationServerSecurityConfigurer
from guniflask.oauth2_config.client_details_service_configurer import ClientDetailsServiceConfigurer
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.beans.factory_hook import SmartInitializingSingleton

__all__ = ['AuthorizationServerConfigurer',
           'AuthorizationServerEndpointsConfiguration',
           'AuthorizationServerSecurityConfiguration']


class AuthorizationServerConfigurer:
    def configure_endpoints(self, endpoints: AuthorizationServerEndpointsConfigurer):
        pass

    def configure_client_details_service(self, clients: ClientDetailsServiceConfigurer):
        pass

    def configure_security(self, security: AuthorizationServerSecurityConfigurer):
        pass


@configuration
class AuthorizationServerEndpointsConfiguration:
    def __init__(self, client_details_service: ClientDetailsService,
                 configurer: AuthorizationServerConfigurer = None):
        self.client_details_service = client_details_service
        self.endpoints_configurer = AuthorizationServerEndpointsConfigurer(client_details_service)
        if configurer:
            configurer.configure_endpoints(self.endpoints_configurer)

    @bean
    def token_endpoint(self) -> TokenEndpoint:
        token_endpoint = TokenEndpoint(self.endpoints_configurer.get_token_granter(), self.client_details_service)
        token_endpoint.oauth2_request_factory = self.endpoints_configurer.get_request_factory()
        token_endpoint.oauth2_request_validator = self.endpoints_configurer.get_request_validator()
        return token_endpoint

    @bean
    def token_key_endpoint(self) -> TokenKeyEndpoint:
        access_token_converter = self.endpoints_configurer.get_access_token_converter()
        if isinstance(access_token_converter, JwtAccessTokenConverter):
            token_key_endpoint = TokenKeyEndpoint(access_token_converter)
            return token_key_endpoint


@configuration
class AuthorizationServerSecurityConfiguration(SmartInitializingSingleton):
    def __init__(self, authentication_manager: AuthenticationManager,
                 configurer: AuthorizationServerConfigurer = None):
        self.authentication_manager = authentication_manager
        self.security_configurer = AuthorizationServerSecurityConfigurer(authentication_manager)
        if configurer:
            configurer.configure_security(self.security_configurer)

    def after_singletons_instantiated(self):
        self.configure()

    def configure(self):
        self.security_configurer.configure()
