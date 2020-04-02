# coding=utf-8

from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.token_granter import AbstractTokenGranter
from guniflask.oauth2.token_service import AuthorizationServerTokenServices
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.oauth2.request_factory import OAuth2RequestFactory
from guniflask.oauth2.request import TokenRequest
from guniflask.oauth2.client_details import ClientDetails
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.authentication_token import UserAuthentication
from guniflask.oauth2.errors import InvalidGrantError
from guniflask.security.errors import BadCredentialsError

__all__ = ['PasswordTokenGranter']


class PasswordTokenGranter(AbstractTokenGranter):
    GRANT_TYPE = 'password'

    def __init__(self, authentication_manager: AuthenticationManager,
                 token_services: AuthorizationServerTokenServices,
                 client_details_service: ClientDetailsService,
                 request_factory: OAuth2RequestFactory):
        super().__init__(token_services, client_details_service, request_factory, self.GRANT_TYPE)
        self.authentication_manager = authentication_manager

    def _get_oauth2_authentication(self, token_request: TokenRequest, client: ClientDetails) -> OAuth2Authentication:
        parameters = token_request.request_parameters
        username = parameters.get('username')
        password = parameters.get('password')
        parameters.pop('password')

        user_auth = UserAuthentication(username, credentials=password)
        user_auth.details = parameters
        try:
            user_auth = self.authentication_manager.authenticate(user_auth)
        except BadCredentialsError as e:
            raise InvalidGrantError(e)
        if user_auth is None or not user_auth.is_authenticated:
            raise InvalidGrantError('Could not authenticate user: {}'.format(username))
        oauth2_request = self.request_factory.create_oauth2_request_from_token_request(token_request, client)
        return OAuth2Authentication(oauth2_request, user_auth)
