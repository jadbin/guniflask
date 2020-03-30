# coding=utf-8

from guniflask.security.basic_authentication_filter import BasicAuthenticationFilter
from guniflask.security_config.security_configurer import SecurityConfigurerAdapter
from guniflask.security_config.web_security_builder import WebSecurityBuilder
from guniflask.security.authentication_manager import AuthenticationManager

__all__ = ['HttpBasicConfigurer']


class HttpBasicConfigurer(SecurityConfigurerAdapter):

    def configure(self, web_security: WebSecurityBuilder):
        authentication_manager = web_security.get_shared_object(AuthenticationManager)
        basic_auth_filter = BasicAuthenticationFilter(authentication_manager)
        web_security.add_before_request_filter(basic_auth_filter)
