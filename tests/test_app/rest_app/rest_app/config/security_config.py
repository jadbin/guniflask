from guniflask.context import configuration
from guniflask.security_config import WebSecurityConfigurer, HttpSecurity

from .jwt_config import JwtConfigurer


@configuration
class SecurityConfiguration(WebSecurityConfigurer):

    def configure_http(self, http: HttpSecurity):
        """Configure http security here"""
        http.apply(JwtConfigurer())
