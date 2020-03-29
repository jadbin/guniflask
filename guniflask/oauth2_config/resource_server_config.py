# coding=utf-8

from abc import ABCMeta, abstractmethod
from typing import List

from guniflask.context.annotation import configuration
from guniflask.oauth2.token_service import ResourceServerTokenServices
from guniflask.oauth2.token_store import TokenStore
from guniflask.oauth2_config.authorization_server_config import AuthorizationServerEndpointsConfiguration
from guniflask.beans.factory_hook import SmartInitializingSingleton
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2_config.resource_server_configurer import ResourceServerSecurityConfigurer

__all__ = ['ResourceServerConfigurer', 'ResourceServerConfigurerAdapter', 'ResourceServerConfiguration']


class ResourceServerConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def configure(self, resources: ResourceServerSecurityConfigurer):
        pass


class ResourceServerConfigurerAdapter(ResourceServerConfigurer):
    def configure(self, resources: ResourceServerSecurityConfigurer):
        pass


@configuration
class ResourceServerConfiguration(SmartInitializingSingleton):
    def __init__(self, configurers: List[ResourceServerConfigurer] = None,
                 token_store: TokenStore = None,
                 token_services: ResourceServerTokenServices = None,
                 endpoints: AuthorizationServerEndpointsConfiguration = None,
                 client_details_service: ClientDetailsService = None):
        self.configurers = configurers
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

        if self.configurers:
            for c in self.configurers:
                c.configure(resources)
        # do configure
        resources.configure()
