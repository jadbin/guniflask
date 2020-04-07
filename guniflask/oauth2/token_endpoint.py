# coding=utf-8

from flask import jsonify

from guniflask.web.bind_annotation import blueprint, get_route, post_route
from guniflask.oauth2.abstract_endpoint import AbstractEndpoint
from guniflask.oauth2.token_converter import JwtAccessTokenConverter
from guniflask.oauth2.errors import InvalidClientError, InvalidRequestError, InvalidGrantError, \
    UnsupportedGrantTypeError, OAuth2AccessDeniedError, OAuth2Error
from guniflask.security.errors import InsufficientAuthenticationError, AuthenticationError
from guniflask.security.context import SecurityContext
from guniflask.security.authentication import Authentication
from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.oauth2.request_factory import DefaultOAuth2RequestValidator
from guniflask.oauth2.oauth2_utils import OAuth2Utils
from guniflask.oauth2.token import OAuth2AccessToken
from guniflask.oauth2.token_granter import TokenGranter
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.web.filter_annotation import error_handler

__all__ = ['TokenEndpoint', 'TokenKeyEndpoint']


@blueprint
class TokenEndpoint(AbstractEndpoint):

    def __init__(self, token_granter: TokenGranter, client_details_service: ClientDetailsService):
        super().__init__(token_granter, client_details_service)
        self.oauth2_request_validator = DefaultOAuth2RequestValidator()

    @post_route('/oauth/token')
    def post_access_token(self):
        auth = SecurityContext.get_authentication()
        if auth is None:
            raise InsufficientAuthenticationError('Authentication required')

        client_id = self._get_client_id(auth)
        authenticated_client = self.client_details_service.load_client_details_by_client_id(client_id)

        parameters = OAuth2Utils.get_request_parameters()
        token_request = self.oauth2_request_factory.create_token_request(parameters, authenticated_client)
        if client_id:
            if client_id != token_request.client_id:
                raise InvalidClientError('Given client ID does not match authenticated client')
        self.oauth2_request_validator.validate_scope(token_request, authenticated_client)
        if not token_request.grant_type:
            raise InvalidRequestError('Missing grant type')
        if token_request.grant_type == 'implicit':
            raise InvalidGrantError('Implicit grant type not supported from token endpoint')

        if self._is_auth_code_request(parameters):
            # The scope was requested or determined during the authorization step
            if token_request.scope:
                token_request.scope = set()
        if self._is_refresh_token_request(parameters):
            # A refresh token has its own default scopes, so we should ignore any added by the factory here
            token_request.scope = OAuth2Utils.parse_parameter_list(parameters.get(OAuth2Utils.SCOPE))

        token = self.token_granter.grant(token_request.grant_type, token_request)
        if token is None:
            raise UnsupportedGrantTypeError('Unsupported grant type: {}'.format(token_request.grant_type))
        return self._get_response(token)

    def _get_client_id(self, auth: Authentication):
        if not auth.is_authenticated:
            raise InvalidClientError('The client is not authenticated')
        client_id = auth.name
        if isinstance(auth, OAuth2Authentication):
            client_id = auth.oauth2_request.client_id
        return client_id

    def _is_auth_code_request(self, parameters: dict):
        return parameters.get('grant_type') == 'authorization_code' and parameters.get('code') is not None

    def _is_refresh_token_request(self, parameters: dict):
        return parameters.get('grant_type') == 'refresh_token' and parameters.get('refresh_token') is not None

    def _get_response(self, token: OAuth2AccessToken):
        resp = jsonify(token.to_dict())
        resp.headers['Cache-Control'] = 'no-store'
        resp.headers['Pragma'] = 'no-cache'
        return resp

    @error_handler(OAuth2Error)
    def handle_oauth2_error(self, e):
        return str(e), 400

    @error_handler(AuthenticationError)
    def handle_authentication_error(self, e):
        return str(e), 400


@blueprint
class TokenKeyEndpoint:
    def __init__(self, token_converter: JwtAccessTokenConverter):
        self.token_converter = token_converter

    @get_route('/oauth/token_key')
    def get_token_key(self):
        auth = SecurityContext.get_authentication()
        if (auth is None or not auth.is_authenticated) and not self.token_converter.is_public:
            raise OAuth2AccessDeniedError('Authentication required to see a shared key')
        return jsonify(self.token_converter.get_key())

    @error_handler(OAuth2Error)
    def handle_oauth2_error(self, e):
        return str(e), 400
