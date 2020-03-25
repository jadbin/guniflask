# coding=utf-8

from functools import partial

from flask import current_app

from guniflask.context.annotation import configuration
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.oauth2.token_service import ResourceServerTokenServices, DefaultTokenServices
from guniflask.oauth2.token_store import TokenStore
from guniflask.oauth2.token_extractor import TokenExtractor, BearerTokenExtractor
from guniflask.oauth2_config.authorization_server_endpoints import AuthorizationServerEndpointsConfiguration
from guniflask.beans.factory_hook import SmartInitializingSingleton
from guniflask.oauth2.authentication_manager import OAuth2AuthenticationManager
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.security.context import SecurityContext

__all__ = ['ResourceServerConfigurer', 'ResourceServerSecurityConfigurer', 'ResourceServerConfiguration']


class ResourceServerSecurityConfigurer:
    def __init__(self):
        self.authentication_manager: AuthenticationManager = None
        self.resource_token_services: ResourceServerTokenServices = None
        self.token_store: TokenStore = None
        self.client_details_service: ClientDetailsService = None
        self.resource_id: str = 'oauth2-resource'
        self.token_extractor: TokenExtractor = None

    def configure(self):
        token_extractor = self._get_token_extractor()
        authentication_manager = self._get_oauth2_authentication_manager()
        current_app.before_request(partial(self._do_authentication_filter, authentication_manager, token_extractor))

    def _do_authentication_filter(self, authentication_manager: OAuth2AuthenticationManager,
                                  token_extractor: TokenExtractor):
        auth = token_extractor.extract()
        if auth is not None:
            user_auth = authentication_manager.authenticate(auth)
            SecurityContext.set_authentication(user_auth)

    def _get_oauth2_authentication_manager(self) -> OAuth2AuthenticationManager:
        if self.authentication_manager and isinstance(self.authentication_manager, OAuth2AuthenticationManager):
            return self.authentication_manager
        authentication_manager = OAuth2AuthenticationManager(self._get_resource_token_services())
        authentication_manager.resource_id = self.resource_id
        authentication_manager.client_details_service = self.client_details_service

    def _get_resource_token_services(self) -> ResourceServerTokenServices:
        if self.resource_token_services is None:
            token_services = DefaultTokenServices(self._get_token_store())
            token_services.client_details_service = self._get_client_details_service()
            token_services.support_refresh_token = True
            self.resource_token_services = token_services
        return self.resource_token_services

    def _get_client_details_service(self):
        return self.client_details_service

    def _get_token_extractor(self):
        if self.token_extractor is None:
            self.token_extractor = BearerTokenExtractor()
        return self.token_extractor

    def _get_token_store(self):
        assert self.token_store is not None, 'Token store is required'
        return self.token_store


class ResourceServerConfigurer:
    def configure(self, resources: ResourceServerSecurityConfigurer):
        pass


@configuration
class ResourceServerConfiguration(SmartInitializingSingleton):
    def __init__(self, configurer: ResourceServerConfigurer = None,
                 token_store: TokenStore = None,
                 token_services: ResourceServerTokenServices = None,
                 endpoints: AuthorizationServerEndpointsConfiguration = None,
                 client_details_service: ClientDetailsService = None):
        self.configurer = configurer
        self.token_store = token_store
        self.token_services = token_services
        self.endpoints = endpoints
        self.client_details_service = client_details_service

    def after_singletons_instantiated(self):
        self.configure()

    def configure(self):
        resources = ResourceServerSecurityConfigurer()
        if self.token_services:
            resources.resource_token_services = self.token_services
        else:
            if self.token_store:
                resources.token_store = self.token_store
            elif self.endpoints:
                resources.token_store = self.endpoints.endpoints_configurer.token_store
        resources.client_details_service = self.client_details_service

        if self.configurer:
            self.configurer.configure(resources)
        # do configure
        resources.configure()
