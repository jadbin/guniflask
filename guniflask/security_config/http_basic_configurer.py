# coding=utf-8

from guniflask.security.basic_authentication_filter import BasicAuthenticationFilter
from guniflask.security_config.security_configurer import SecurityConfigurer
from guniflask.security_config.http_security_builder import HttpSecurityBuilder
from guniflask.security.authentication_manager import AuthenticationManager


class HttpBasicConfigurer(SecurityConfigurer):

    def configure(self, http: HttpSecurityBuilder):
        authentication_manager = http.get_shared_object(AuthenticationManager)
        basic_auth_filter = BasicAuthenticationFilter(authentication_manager)
        http.add_request_filter(basic_auth_filter)
