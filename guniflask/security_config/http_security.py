# coding=utf-8

from guniflask.security_config.configured_security_builder import ConfiguredSecurityBuilder
from guniflask.security_config.authentication_manager_builder import AuthenticationManagerBuilder

__all__ = ['HttpSecurity']


class HttpSecurity(ConfiguredSecurityBuilder):
    def __init__(self, authentication_builder: AuthenticationManagerBuilder):
        super().__init__()
        assert authentication_builder is not None, 'Authentication builder is required'
        self.set_shared_object(AuthenticationManagerBuilder, authentication_builder)

    def _perform_build(self):
        pass
