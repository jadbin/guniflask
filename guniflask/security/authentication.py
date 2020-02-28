# coding=utf-8


from flask import current_app, request, _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.token import AccessToken
from guniflask.security.request import OAuth2Request

__all__ = ['current_auth', 'auth_manager', 'Authentication', 'OAuth2Authentication', 'UserAuthentication',
           'AuthenticationManager', 'BearerTokenExtractor', 'PreAuthenticatedToken']

auth_manager = LocalProxy(lambda: current_app.extensions['authentication_manager'])


def _load_authentication():
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'authentication'):
            return None
        return ctx.authentication


current_auth = LocalProxy(_load_authentication)


class Authentication:
    def __init__(self, authorities=None):
        self._authorities = set()
        if authorities is not None:
            self._authorities.update(authorities)
        self._details = None
        self._authenticated = False

    @property
    def principal(self):
        raise NotImplemented

    @property
    def credentials(self):
        raise NotImplemented

    def authenticate(self, value):
        self._authenticated = value

    @property
    def is_authenticated(self):
        return self._authenticated

    @property
    def authorities(self):
        return self.authorities

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, details):
        self._details = details


class UserAuthentication(Authentication):
    def __init__(self, principal, credentials=None, authorities=None):
        super().__init__(authorities=authorities)
        self._principal = principal
        self._credentials = credentials

    @property
    def principal(self):
        return self._principal

    @property
    def credentials(self):
        return self._credentials


class OAuth2Authentication(Authentication):
    def __init__(self, stored_request: OAuth2Request, user_authentication: Authentication = None):
        authorities = None
        if user_authentication is not None:
            authorities = user_authentication.authorities
        super().__init__(authorities=authorities)
        self._stored_request = stored_request
        self._user_authentication = user_authentication

    @property
    def principal(self):
        if self._user_authentication is None:
            return self._stored_request.client_id
        return self.user_authentication.principal

    @property
    def credentials(self):
        return None

    @property
    def stored_request(self):
        return self._stored_request

    @property
    def user_authentication(self):
        return self._user_authentication


class AuthenticationManager:
    def __init__(self):
        self.token_service = None
        self.token_extractor = BearerTokenExtractor()

    def init_app(self, app):
        app.extensions['authentication_manager'] = self
        app.before_request(self.do_authentication_filter)

    def authenticate(self, authentication):
        # TODO
        pass

    def do_authentication_filter(self):
        authentication = self.token_extractor.extract()
        auth_result = self.authenticate(authentication)
        ctx = _request_ctx_stack.top
        if ctx is not None:
            ctx.authentication = auth_result


class BearerTokenExtractor:
    def extract(self):
        token = self._extract_token_from_header()
        if token is None:
            token = self._extract_token_from_query()
        if token is not None:
            return PreAuthenticatedToken(token)

    @staticmethod
    def _extract_token_from_header():
        auth = request.headers.get('Authorization')
        if auth is not None and auth.lower().startswith(AccessToken.BEARER_TYPE.lower()):
            return auth.split(' ', 1)[1]

    @staticmethod
    def _extract_token_from_query():
        return request.args.get(AccessToken.ACCESS_TOKEN)


class PreAuthenticatedToken(Authentication):
    def __init__(self, token):
        super().__init__()
        self._token = token

    @property
    def principal(self):
        return self._token

    @property
    def credentials(self):
        return None
