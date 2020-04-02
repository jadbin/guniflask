# coding=utf-8

from guniflask.context import configuration
from guniflask.config import settings
from guniflask.security_config import WebSecurityConfigurer, HttpSecurity, enable_web_security

from .jwt_config import JwtConfigurer


@configuration
@enable_web_security
class SecurityConfiguration(WebSecurityConfigurer):

    def configure_http(self, http: HttpSecurity):
        jwt = settings.get_by_prefix('guniflask.jwt')
        if jwt:
            http.apply(JwtConfigurer(jwt))

        cors = settings.get_by_prefix('guniflask.cors')
        if cors:
            http.cors(cors)
