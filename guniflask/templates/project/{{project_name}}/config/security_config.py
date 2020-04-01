# coding=utf-8

from guniflask.context import configuration
from guniflask.security import JwtManager, SecurityContext
from guniflask.config import settings
from guniflask.web import RequestFilter, CorsFilter
from guniflask.oauth2 import BearerTokenExtractor
from guniflask.security_config import WebSecurityConfigurerAdapter, HttpSecurity, enable_web_security


@configuration
@enable_web_security
class SecurityConfiguration(WebSecurityConfigurerAdapter):

    def _configure_http(self, http: HttpSecurity):
        jwt_filter = self._get_jwt_filter()
        if jwt_filter:
            http.add_request_filter(jwt_filter)

        cors_filter = self._get_cors_filter()
        if cors_filter:
            http.add_request_filter(cors_filter)

    def _get_jwt_filter(self):
        jwt_config = settings.get_by_prefix('guniflask.jwt')
        if jwt_config and isinstance(jwt_config, dict):
            jwt_manager = JwtManager(**jwt_config)
            jwt_filter = JwtFilter(jwt_manager)
            return jwt_filter

    def _get_cors_filter(self):
        cors = settings.get_by_prefix('guniflask.cors')
        if cors:
            if isinstance(cors, dict):
                cors_filter = CorsFilter(**cors)
            else:
                cors_filter = CorsFilter()
            return cors_filter


class JwtFilter(RequestFilter):
    def __init__(self, jwt_manager: JwtManager):
        self.jwt_manager = jwt_manager
        self.token_extractor = BearerTokenExtractor()

    def before_request(self):
        auth = self.token_extractor.extract()
        if auth is not None:
            user_auth = self.jwt_manager.authenticate(auth)
            SecurityContext.set_authentication(user_auth)
