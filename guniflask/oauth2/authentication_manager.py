# coding=utf-8

from flask import request, _request_ctx_stack

from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.preauth_token import PreAuthenticatedToken
from guniflask.oauth2.token import OAuth2AccessToken
from guniflask.oauth2.token_service import ResourceServerTokenServices

__all__ = ['OAuth2AuthenticationManager', 'BearerTokenExtractor']


class OAuth2AuthenticationManager(AuthenticationManager):
    def __init__(self):
        self.token_service: ResourceServerTokenServices = None
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
