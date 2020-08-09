# coding=utf-8

from typing import List

from guniflask.context.annotation import configuration
from guniflask.oauth2.token_service import ResourceServerTokenServices
from guniflask.oauth2.token_store import TokenStore
from guniflask.oauth2_config.authorization_server_config import AuthorizationServerEndpointsConfiguration
from guniflask.oauth2_config.resource_server_configurer import ResourceServerConfigurer, \
    ResourceServerSecurityConfigurer
from guniflask.security_config.http_security import HttpSecurity
from guniflask.security_config.web_security_configurer import WebSecurityConfigurer

__all__ = ['ResourceServerConfiguration']


@configuration
class ResourceServerConfiguration(WebSecurityConfigurer):
    def __init__(self, configurers: List[ResourceServerConfigurer] = None,
                 token_store: TokenStore = None,
                 token_services: ResourceServerTokenServices = None,
                 endpoints: AuthorizationServerEndpointsConfiguration = None):
        super().__init__()
        self._configurers = configurers
        self._token_store = token_store
        self._token_services = token_services
        self._endpoints = endpoints

    def configure_http(self, http: HttpSecurity):
        resources = ResourceServerSecurityConfigurer()
        if self._token_services:
            resources.with_token_services(self._token_services)
        else:
            if self._token_store:
                resources.with_token_store(self._token_store)
            elif self._endpoints:
                resources.with_token_store(self._endpoints.endpoints_configurer.token_store)

        if self._configurers:
            for c in self._configurers:
                c.configure_security(resources)

        http.apply(resources)

        if self._configurers:
            for c in self._configurers:
                c.configure_http(http)
