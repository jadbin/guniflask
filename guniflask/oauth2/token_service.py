# coding=utf-8

import datetime as dt
from typing import Optional
import uuid
from abc import ABCMeta, abstractmethod

from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.token import OAuth2AccessToken, OAuth2RefreshToken
from guniflask.oauth2.token_store import TokenStore
from guniflask.oauth2.token_converter import TokenEnhancer
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.request import TokenRequest, OAuth2Request
from guniflask.oauth2.errors import InvalidTokenError, InvalidGrantError, InvalidScopeError, ClientRegistrationError
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.preauth_token import PreAuthenticatedToken
from guniflask.beans.factory_hook import InitializingBean

__all__ = ['AuthorizationServerTokenServices',
           'ResourceServerTokenServices',
           'ConsumerTokenServices',
           'DefaultTokenServices']


class AuthorizationServerTokenServices(metaclass=ABCMeta):
    @abstractmethod
    def create_access_token(self, authentication: OAuth2Authentication = None) -> OAuth2AccessToken:
        pass

    @abstractmethod
    def refresh_access_token(self, refresh_token_value: str, token_request: TokenRequest) -> OAuth2AccessToken:
        pass

    @abstractmethod
    def get_access_token(self, authentication) -> OAuth2AccessToken:
        pass


class ResourceServerTokenServices(metaclass=ABCMeta):
    @abstractmethod
    def load_authentication(self, access_token_value: str) -> OAuth2Authentication:
        pass

    @abstractmethod
    def read_access_token(self, access_token_value: str) -> OAuth2AccessToken:
        pass


class ConsumerTokenServices(metaclass=ABCMeta):
    @abstractmethod
    def revoke_token(self, access_token_value: str):
        pass


class DefaultTokenServices(AuthorizationServerTokenServices, ResourceServerTokenServices, ConsumerTokenServices,
                           InitializingBean):
    """
    Base implementation for token services using random UUID values for the access token and refresh token values.
    """

    def __init__(self, token_store: TokenStore):
        self.token_store = token_store
        self.token_enhancer: TokenEnhancer = None
        self.client_details_service: ClientDetailsService = None
        self.access_token_expires_in = 24 * 60 * 60
        self.refresh_token_expires_in = 365 * 24 * 60 * 60
        self.support_refresh_token = False
        self.authentication_manager: AuthenticationManager = None

    def after_properties_set(self):
        assert self.token_store is not None, 'Token store must be set'

    def create_access_token(self, authentication: OAuth2Authentication = None) -> OAuth2AccessToken:
        existing_access_token = self.token_store.get_access_token(authentication)
        refresh_token = None
        if existing_access_token is not None:
            if existing_access_token.is_expired:
                if existing_access_token.refresh_token is not None:
                    refresh_token = existing_access_token.refresh_token
                    self.token_store.remove_refresh_token(refresh_token)
                self.token_store.remove_access_token(existing_access_token)
            else:
                self.token_store.store_access_token(existing_access_token, authentication)
                return existing_access_token

        if refresh_token is None:
            refresh_token = self._create_refresh_token(authentication)
        elif refresh_token.is_expired:
            refresh_token = self._create_refresh_token(authentication)

        access_token = self._do_create_access_token(authentication, refresh_token)
        self.token_store.store_access_token(access_token, authentication)
        if access_token.refresh_token is not None:
            self.token_store.store_refresh_token(refresh_token, authentication)
        return access_token

    def refresh_access_token(self, refresh_token_value: str, token_request: TokenRequest) -> OAuth2AccessToken:
        if not self.support_refresh_token:
            raise InvalidGrantError('Invalid refresh token: {}'.format(refresh_token_value))
        refresh_token = self.token_store.read_refresh_token(refresh_token_value)
        if refresh_token is None:
            raise InvalidGrantError('Invalid refresh token: {}'.format(refresh_token_value))

        authentication = self.token_store.read_authentication_for_refresh_token(refresh_token)
        if self.authentication_manager is not None and not authentication.is_client_only:
            user = PreAuthenticatedToken(authentication.user_authentication, authorities=authentication.authorities)
            user = self.authentication_manager.authenticate(user)
            details = authentication.details
            authentication = OAuth2Authentication(authentication.oauth2_request, user)
            authentication.details = details
        client_id = authentication.oauth2_request.client_id
        if client_id is None or client_id != token_request.client_id:
            raise InvalidGrantError('Wrong client for this refresh token: {}'.format(refresh_token_value))

        self.token_store.remove_access_token_using_refresh_token(refresh_token)
        if refresh_token.is_expired:
            self.token_store.remove_refresh_token(refresh_token)
            raise InvalidTokenError('Refresh token expired: {}'.format(refresh_token_value))
        authentication = self._create_refreshed_authentication(authentication, token_request)
        access_token = self._do_create_access_token(authentication, refresh_token)
        self.token_store.store_access_token(access_token, authentication)
        return access_token

    def get_access_token(self, authentication) -> OAuth2AccessToken:
        return self.token_store.get_access_token(authentication)

    def load_authentication(self, access_token_value: str) -> OAuth2Authentication:
        access_token = self.token_store.read_access_token(access_token_value)
        if access_token is None:
            raise InvalidTokenError('Invalid access token: {}'.format(access_token_value))
        elif access_token.is_expired:
            self.token_store.remove_access_token(access_token)
            raise InvalidTokenError('Access token expired: {}'.format(access_token_value))

        result = self.token_store.read_authentication(access_token)
        if result is None:
            raise InvalidTokenError('Invalid access token: {}'.format(access_token_value))
        if self.client_details_service is not None:
            client_id = result.oauth2_request.client_id
            try:
                self.client_details_service.load_client_details_by_client_id(client_id)
            except ClientRegistrationError:
                raise InvalidTokenError('Client not valid: {}'.format(client_id))
        return result

    def read_access_token(self, access_token_value: str) -> OAuth2AccessToken:
        return self.token_store.read_access_token(access_token_value)

    def revoke_token(self, access_token_value: str):
        access_token = self.token_store.read_access_token(access_token_value)
        if access_token:
            if access_token.refresh_token:
                self.token_store.remove_refresh_token(access_token.refresh_token)
            self.token_store.remove_access_token(access_token)

    def _create_refresh_token(self, authentication: OAuth2Authentication) -> Optional[OAuth2RefreshToken]:
        if not self._is_support_refresh_token(authentication.oauth2_request):
            return None
        expires_in = self._get_refresh_token_expires_in(authentication.oauth2_request)
        value = uuid.uuid4().hex
        if expires_in <= 0:
            expiration = None
        else:
            expiration = dt.datetime.now() + dt.timedelta(seconds=expires_in)
        return OAuth2RefreshToken(value, expiration=expiration)

    def _is_support_refresh_token(self, client_auth: OAuth2Request) -> bool:
        if self.client_details_service is not None:
            client = self.client_details_service.load_client_details_by_client_id(client_auth.client_id)
            return 'refresh_token' in client.grant_types
        return self.support_refresh_token

    def _get_refresh_token_expires_in(self, client_auth: OAuth2Request) -> int:
        if self.client_details_service is not None:
            client = self.client_details_service.load_client_details_by_client_id(client_auth.client_id)
            expires_in = client.refresh_token_expires_in
            if expires_in is not None:
                return expires_in
        return self.refresh_token_expires_in

    def _do_create_access_token(self, authentication: OAuth2Authentication,
                                refresh_token: OAuth2RefreshToken) -> OAuth2AccessToken:
        token = OAuth2AccessToken(uuid.uuid4().hex)
        expires_in = self._get_access_token_expires_in(authentication.oauth2_request)
        if expires_in <= 0:
            expiration = None
        else:
            expiration = dt.datetime.now() + dt.timedelta(seconds=expires_in)
        token.expiration = expiration
        token.refresh_token = refresh_token
        token.scope = authentication.oauth2_request.scope

        if self.token_enhancer is not None:
            return self.token_enhancer.enhance(token, authentication)
        return token

    def _get_access_token_expires_in(self, client_auth: OAuth2Request) -> int:
        if self.client_details_service is not None:
            client = self.client_details_service.load_client_details_by_client_id(client_auth.client_id)
            expires_in = client.access_token_expires_in
            if expires_in is not None:
                return expires_in
        return self.access_token_expires_in

    def _create_refreshed_authentication(self, authentication: OAuth2Authentication,
                                         request: TokenRequest) -> OAuth2Authentication:
        scope = request.scope
        client_auth = authentication.oauth2_request.do_refresh(request)
        if scope:
            original_scope = client_auth.scope
            if original_scope is None or not original_scope.issuperset(scope):
                raise InvalidScopeError('Unable to narrow the scope of the client authentication to: {}'.format(scope))
            else:
                client_auth = client_auth.narrow_scope(scope)
        narrowed = OAuth2Authentication(client_auth, authentication.user_authentication)
        return narrowed
