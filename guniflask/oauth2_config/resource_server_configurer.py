# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.oauth2.token_service import ResourceServerTokenServices, DefaultTokenServices
from guniflask.oauth2.token_store import TokenStore
from guniflask.oauth2.token_extractor import TokenExtractor
from guniflask.oauth2.authentication_manager import OAuth2AuthenticationManager
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.security_config.security_configurer import SecurityConfigurerAdapter
from guniflask.oauth2.authentication_filter import OAuth2AuthenticationFilter
from guniflask.security_config.http_security import HttpSecurity

__all__ = ['ResourceServerConfigurer',
           'ResourceServerConfigurerAdapter',
           'ResourceServerSecurityConfigurer']


class ResourceServerSecurityConfigurer(SecurityConfigurerAdapter):
    def __init__(self):
        super().__init__()
        self._authentication_manager: AuthenticationManager = None
        self._resource_token_services: ResourceServerTokenServices = None
        self._token_store: TokenStore = None
        self._resource_id: str = 'oauth2-resource'
        self._token_extractor: TokenExtractor = None

    @property
    def token_store(self) -> TokenStore:
        return self._token_store

    def with_token_store(self, token_store: TokenStore) -> 'ResourceServerSecurityConfigurer':
        self._token_store = token_store
        return self

    def with_token_extractor(self, token_extractor: TokenExtractor) -> 'ResourceServerSecurityConfigurer':
        self._token_extractor = token_extractor
        return self

    def with_authentication_manager(self, authentication_manager: AuthenticationManager
                                    ) -> 'ResourceServerSecurityConfigurer':
        self._authentication_manager = authentication_manager
        return self

    def with_token_services(self, token_services: ResourceServerTokenServices) -> 'ResourceServerSecurityConfigurer':
        self._resource_token_services = token_services
        return self

    def with_resource_id(self, resource_id: str):
        self._resource_id = resource_id
        return self

    def configure(self, http: HttpSecurity):
        authentication_manager = self._get_oauth2_authentication_manager()
        authentication_filter = OAuth2AuthenticationFilter()
        authentication_filter.authentication_manager = authentication_manager
        if self._token_extractor is not None:
            authentication_filter.token_extractor = self._token_extractor
        http.add_request_filter(authentication_filter)

    def _get_oauth2_authentication_manager(self) -> AuthenticationManager:
        if self._authentication_manager:
            if isinstance(self._authentication_manager, OAuth2AuthenticationManager):
                authentication_manager = self._authentication_manager
            else:
                return self._authentication_manager
        else:
            authentication_manager = OAuth2AuthenticationManager()

        authentication_manager.resource_id = self._resource_id
        authentication_manager.token_services = self._get_resource_token_services()
        authentication_manager.client_details_service = self._get_client_details_service()
        return authentication_manager

    def _get_resource_token_services(self) -> ResourceServerTokenServices:
        if self._resource_token_services is None:
            token_services = DefaultTokenServices(self._get_token_store())
            token_services.support_refresh_token = True
            token_services.client_details_service = self._get_client_details_service()
            self.resource_token_services = token_services
        return self.resource_token_services

    def _get_client_details_service(self) -> ClientDetailsService:
        http: HttpSecurity = self.builder
        return http.get_shared_object(ClientDetailsService)

    def _get_token_store(self):
        assert self.token_store is not None, 'Token store is required'
        return self.token_store


class ResourceServerConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def configure_security(self, resources: ResourceServerSecurityConfigurer):
        pass

    @abstractmethod
    def configure_http(self, http: HttpSecurity):
        pass


class ResourceServerConfigurerAdapter(ResourceServerConfigurer):
    def configure_security(self, resources: ResourceServerSecurityConfigurer):
        pass

    def configure_http(self, http: HttpSecurity):
        pass
