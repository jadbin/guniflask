# coding=utf-8

from abc import ABCMeta, abstractmethod
from typing import Collection

from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.token_service import AuthorizationServerTokenServices, DefaultTokenServices
from guniflask.oauth2.token_store import TokenStore, JwtTokenStore
from guniflask.oauth2.token_converter import TokenEnhancer, AccessTokenConverter, JwtAccessTokenConverter, \
    DefaultAccessTokenConverter
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.oauth2.request_factory import OAuth2RequestFactory, OAuth2RequestValidator, \
    DefaultOAuth2RequestValidator, DefaultOAuth2RequestFactory
from guniflask.oauth2.token_granter import TokenGranter, CompositeTokenGranter
from guniflask.oauth2.password_grant import PasswordTokenGranter
from guniflask.oauth2.client_grant import ClientCredentialsTokenGranter
from guniflask.oauth2.refresh_grant import RefreshTokenGranter
from guniflask.security_config.http_security import HttpSecurity
from guniflask.security.password_encoder import PasswordEncoder
from guniflask.oauth2.client_details_user_details_service import ClientDetailsUserDetailsService
from guniflask.security_config.authentication_manager_builder import AuthenticationManagerBuilder
from guniflask.oauth2.client_details_service import InMemoryClientDetailsService
from guniflask.security.user_details_service import UserDetailsService
from guniflask.security_config.security_configurer import SecurityConfigurerAdapter
from guniflask.oauth2_config.client_details_service_configurer import ClientDetailsServiceConfigurer

__all__ = ['AuthorizationServerConfigurer',
           'AuthorizationServerConfigurerAdapter',
           'AuthorizationServerEndpointsConfigurer',
           'AuthorizationServerSecurityConfigurer']


class AuthorizationServerEndpointsConfigurer:
    def __init__(self):
        self._client_details_service: ClientDetailsService = None
        self._token_services: AuthorizationServerTokenServices = None
        self._token_store: TokenStore = None
        self._token_enhancer: TokenEnhancer = None
        self._access_token_converter: AccessTokenConverter = None
        self._token_granter: TokenGranter = None
        self._request_factory: OAuth2RequestFactory = None
        self._request_validator: OAuth2RequestValidator = None
        self._authentication_manager: AuthenticationManager = None
        self._token_services_override = False
        self._user_details_service: UserDetailsService = None
        self._user_details_service_override = False

    @property
    def token_services(self) -> AuthorizationServerTokenServices:
        if self._token_services is None:
            self._token_services = self._create_default_token_services()
        return self._token_services

    @property
    def token_store(self) -> TokenStore:
        return self._get_token_store()

    @property
    def token_enhancer(self) -> TokenEnhancer:
        return self._token_enhancer

    @property
    def access_token_converter(self) -> AccessTokenConverter:
        return self._get_access_token_converter()

    @property
    def client_details_service(self) -> ClientDetailsService:
        return self._get_client_details_service()

    @property
    def oauth2_request_factory(self) -> OAuth2RequestFactory:
        return self._get_request_factory()

    @property
    def oauth2_request_validator(self) -> OAuth2RequestValidator:
        return self._get_request_validator()

    def with_client_details_service(self, client_details_service: ClientDetailsService):
        self._client_details_service = client_details_service
        return self

    def with_token_store(self, token_store: TokenStore) -> 'AuthorizationServerEndpointsConfigurer':
        self._token_store = token_store
        return self

    def with_token_enhancer(self, token_enhancer: TokenEnhancer) -> 'AuthorizationServerEndpointsConfigurer':
        self._token_enhancer = token_enhancer
        return self

    def with_access_token_converter(self, access_token_converter: AccessTokenConverter):
        self._access_token_converter = access_token_converter
        return self

    def with_token_services(self, token_services: AuthorizationServerTokenServices
                            ) -> 'AuthorizationServerEndpointsConfigurer':
        self._token_services = token_services
        if token_services:
            self._token_services_override = True
        return self

    def with_authentication_manager(self, authentication_manager: AuthenticationManager
                                    ) -> 'AuthorizationServerEndpointsConfigurer':
        self._authentication_manager = authentication_manager
        return self

    def with_token_granter(self, token_granter: TokenGranter) -> 'AuthorizationServerEndpointsConfigurer':
        self._token_granter = token_granter
        return self

    def with_request_factory(self, request_factory: OAuth2RequestFactory) -> 'AuthorizationServerEndpointsConfigurer':
        self._request_factory = request_factory
        return self

    def with_request_validator(self, request_validator: OAuth2RequestValidator
                               ) -> 'AuthorizationServerEndpointsConfigurer':
        self._request_validator = request_validator
        return self

    def with_user_details_service(self, user_details_service: UserDetailsService):
        if user_details_service:
            self._user_details_service = user_details_service
            self._user_details_service_override = True
        return self

    @property
    def token_granter(self) -> TokenGranter:
        return self._get_token_granter()

    def _get_token_store(self) -> TokenStore:
        if self._token_store is None:
            access_token_converter = self._get_access_token_converter()
            if isinstance(access_token_converter, JwtAccessTokenConverter):
                self._token_store = JwtTokenStore(access_token_converter)
            else:
                # FIXME: default in memory token store
                self._token_store = None
        return self._token_store

    def _get_token_enhancer(self) -> TokenEnhancer:
        if self._token_enhancer is None:
            access_token_converter = self._get_access_token_converter()
            if isinstance(access_token_converter, JwtAccessTokenConverter):
                self._token_enhancer = access_token_converter
        return self._token_enhancer

    def _get_access_token_converter(self) -> AccessTokenConverter:
        if self._access_token_converter is None:
            self._access_token_converter = DefaultAccessTokenConverter()
        return self._access_token_converter

    def _get_client_details_service(self) -> ClientDetailsService:
        if self._client_details_service is None:
            self._client_details_service = InMemoryClientDetailsService()
        return self._client_details_service

    def _get_token_granter(self) -> TokenGranter:
        if self._token_granter is None:
            self._token_granter = CompositeTokenGranter(self._get_default_token_granters())
        return self._token_granter

    def _get_request_factory(self) -> OAuth2RequestFactory:
        if self._request_factory is None:
            self._request_factory = DefaultOAuth2RequestFactory(self._client_details_service)
        return self._request_factory

    def _get_request_validator(self) -> OAuth2RequestValidator:
        if self._request_validator is None:
            self._request_validator = DefaultOAuth2RequestValidator()
        return self._request_validator

    def _create_default_token_services(self) -> AuthorizationServerTokenServices:
        token_services = DefaultTokenServices(self._get_token_store())
        token_services.support_refresh_token = True
        token_services.token_enhancer = self._get_token_enhancer()
        token_services.client_details_service = self._client_details_service
        return token_services

    def _get_default_token_granters(self) -> Collection[TokenGranter]:
        token_granters = []
        token_services = self.token_services
        request_factory = self._get_request_factory()
        token_granters.append(RefreshTokenGranter(token_services, self._client_details_service, request_factory))
        token_granters.append(ClientCredentialsTokenGranter(token_services,
                                                            self._client_details_service,
                                                            request_factory))
        if self._authentication_manager is not None:
            token_granters.append(PasswordTokenGranter(self._authentication_manager,
                                                       token_services,
                                                       self._client_details_service,
                                                       request_factory))
        return token_granters


class AuthorizationServerSecurityConfigurer(SecurityConfigurerAdapter):
    def __init__(self):
        super().__init__()
        self._password_encoder: PasswordEncoder = None

    def init(self, http: HttpSecurity):
        if self._password_encoder:
            password_encoder = self._get_password_encoder()
            client_details_user_details_service = ClientDetailsUserDetailsService(self._get_client_details_service())
            client_details_user_details_service.set_password_encoder(password_encoder)
            builder: AuthenticationManagerBuilder = http.get_shared_object(AuthenticationManagerBuilder)
            builder \
                .with_user_details_service(client_details_user_details_service) \
                .with_password_encoder(password_encoder)
        else:
            http.with_user_details_service(ClientDetailsUserDetailsService(self._get_client_details_service()))

    def configure(self, http: HttpSecurity):
        pass

    def with_password_encoder(self, password_encoder: PasswordEncoder):
        self._password_encoder = password_encoder
        return self

    def _get_client_details_service(self) -> ClientDetailsService:
        return self.builder.get_shared_object(ClientDetailsService)

    def _get_password_encoder(self) -> PasswordEncoder:
        return NullablePasswordEncoder(self._password_encoder)


class NullablePasswordEncoder(PasswordEncoder):
    def __init__(self, password_encoder: PasswordEncoder):
        self.password_encoder = password_encoder

    def encode(self, raw_password: bytes) -> str:
        return self.password_encoder.encode(raw_password)

    def matches(self, raw_password: bytes, encoded_password: str) -> bool:
        if not encoded_password:
            return True
        return self.password_encoder.matches(raw_password, encoded_password)


class AuthorizationServerConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def configure_endpoints(self, endpoints: AuthorizationServerEndpointsConfigurer):
        pass

    @abstractmethod
    def configure_client_details_service(self, clients: ClientDetailsServiceConfigurer):
        pass

    @abstractmethod
    def configure_security(self, security: AuthorizationServerSecurityConfigurer):
        pass


class AuthorizationServerConfigurerAdapter(AuthorizationServerConfigurer):
    def configure_endpoints(self, endpoints: AuthorizationServerEndpointsConfigurer):
        pass

    def configure_client_details_service(self, clients: ClientDetailsServiceConfigurer):
        pass

    def configure_security(self, security: AuthorizationServerSecurityConfigurer):
        pass
