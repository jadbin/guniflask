from typing import Union

from flask import request
from werkzeug.local import LocalProxy

from guniflask.config import settings
from guniflask.security import JwtManager, SecurityContext
from guniflask.security.authentication import Authentication
from guniflask.security.preauth_token import PreAuthenticatedToken
from guniflask.security_config import SecurityConfigurer, HttpSecurityBuilder
from guniflask.web import RequestFilter

jwt_manager: Union[JwtManager, LocalProxy] = LocalProxy(lambda: settings['jwt_manager'])


class BearerTokenExtractor:
    def extract(self) -> Authentication:
        token = self._extract_token_from_header()
        if token is None:
            token = self._extract_token_from_query()
        if token is not None:
            return PreAuthenticatedToken(token)

    @staticmethod
    def _extract_token_from_header():
        auth = request.headers.get('Authorization')
        if auth is not None and auth.lower().startswith('bearer'):
            return auth.split(' ', 1)[1]

    @staticmethod
    def _extract_token_from_query():
        token = request.args.get('access_token')
        if token is not None:
            return token


class JwtConfigurer(SecurityConfigurer):
    def __init__(self, jwt=None):
        super().__init__()
        self.jwt_filter = None
        if isinstance(jwt, dict):
            settings['jwt_manager'] = JwtManager(**jwt)
            self.jwt_filter = JwtFilter()

    def configure(self, http: HttpSecurityBuilder):
        if self.jwt_filter:
            http.add_request_filter(self.jwt_filter)


class JwtFilter(RequestFilter):
    def __init__(self):
        self.token_extractor = BearerTokenExtractor()

    def before_request(self):
        auth = self.token_extractor.extract()
        if auth is not None:
            user_auth = jwt_manager.authenticate(auth)
            SecurityContext.set_authentication(user_auth)
