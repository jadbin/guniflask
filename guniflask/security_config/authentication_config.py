# coding=utf-8

from guniflask.context.annotation import configuration, bean
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security_config.authentication_manager_builder import AuthenticationManagerBuilder

__all__ = ['AuthenticationConfiguration']


@configuration
class AuthenticationConfiguration:
    def __init__(self):
        self._authentication_manager: AuthenticationManager = None
        self._authentication_manager_initialized = False
        self._authentication_manager_builder = AuthenticationManagerBuilder()

    @bean
    def authentication_manager_builder(self) -> AuthenticationManagerBuilder:
        return self._authentication_manager_builder

    @property
    def authentication_manager(self) -> AuthenticationManager:
        if self._authentication_manager_initialized:
            return self._authentication_manager
        self._authentication_manager = self._authentication_manager_builder.build()
        return self._authentication_manager
