# coding=utf-8

from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.oauth2.token_service import ResourceServerTokenServices
from guniflask.beans.factory_hook import InitializingBean
from guniflask.oauth2.errors import InvalidTokenError, OAuth2AccessDeniedError, ClientRegistrationError
from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.security.context import SecurityContext
from guniflask.oauth2.token_extractor import BearerTokenExtractor

__all__ = ['OAuth2AuthenticationManager']


class OAuth2AuthenticationManager(AuthenticationManager, InitializingBean):
    def __init__(self, token_services: ResourceServerTokenServices):
        self.token_services = token_services
        self.resource_id: str = None
        self.client_details_service: ClientDetailsService = None
        self.token_extractor = BearerTokenExtractor()

    def after_properties_set(self):
        assert self.token_services is not None, 'Token services are required'

    def init_app(self, app):
        app.before_request(self.do_authentication_filter)

    def authenticate(self, authentication):
        if authentication is None:
            raise InvalidTokenError('Token not found')
        token_value = str(authentication.principal)
        auth = self.token_services.load_authentication(token_value)
        if auth is None:
            raise InvalidTokenError('Invalid token: {}'.format(token_value))

        resource_ids = auth.oauth2_request.resource_ids
        if self.resource_id and resource_ids and self.resource_id not in resource_ids:
            raise OAuth2AccessDeniedError(
                'Invalid token does not contain resource id ({})'.format(self.resource_id))
        self._check_client_details(auth)

        auth.details = authentication.details
        auth.authenticate(True)
        return auth

    def do_authentication_filter(self):
        authentication = self.token_extractor.extract()
        auth_result = self.authenticate(authentication)
        SecurityContext.set_authentication(auth_result)

    def _check_client_details(self, auth: OAuth2Authentication):
        if self.client_details_service is not None:
            client_id = auth.oauth2_request.client_id
            try:
                client = self.client_details_service.load_client_details_by_client_id(client_id)
            except ClientRegistrationError:
                raise OAuth2AccessDeniedError('Invalid token contains invalid client id ({})'.format(client_id))
            allowed = client.scope
            for scope in auth.oauth2_request.scope:
                if scope not in allowed:
                    raise OAuth2AccessDeniedError(
                        'Invalid token contains disallowed scope ({}) for this client'.format(scope))
