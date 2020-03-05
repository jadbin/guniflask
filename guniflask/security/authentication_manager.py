# coding=utf-8

from flask import request, _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.authentication import Authentication, PreAuthenticatedToken
from guniflask.security.token import OAuth2AccessToken

__all__ = ['current_auth', 'AuthenticationManager', 'OAuth2AuthenticationManager',
           'BearerTokenExtractor']


def _load_authentication():
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'authentication'):
            return None
        return ctx.authentication


current_auth = LocalProxy(_load_authentication)


class AuthenticationManager:
    def authenticate(self, authentication: Authentication) -> Authentication:
        raise NotImplemented


class OAuth2AuthenticationManager(AuthenticationManager):
    def __init__(self):
        self.token_service = None
        self.token_extractor = BearerTokenExtractor()

    def init_app(self, app):
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
        if auth is not None and auth.lower().startswith(OAuth2AccessToken.BEARER_TYPE.lower()):
            return auth.split(' ', 1)[1]

    @staticmethod
    def _extract_token_from_query():
        return request.args.get(OAuth2AccessToken.ACCESS_TOKEN)
