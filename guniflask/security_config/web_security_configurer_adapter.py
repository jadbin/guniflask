# coding=utf-8

from guniflask.security.authentication import Authentication
from guniflask.security_config.web_security_configurer import WebSecurityConfigurer
from guniflask.security_config.authentication_manager_builder import AuthenticationManagerBuilder
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security_config.web_security import WebSecurity
from guniflask.security_config.http_security import HttpSecurity
from guniflask.security_config.authentication_config import AuthenticationConfiguration
from guniflask.beans.annotation import autowired

__all__ = ['WebSecurityConfigurerAdapter']


class WebSecurityConfigurerAdapter(WebSecurityConfigurer):
    def __init__(self):
        self._authentication_configuration: AuthenticationConfiguration = None
        self._authentication_builder = AuthenticationManagerBuilder()
        self._local_authentication_builder = AuthenticationManagerBuilder()
        self._enable_local_authentication = False
        self._authentication_manager: AuthenticationManager = None
        self._authentication_manager_initialized = False
        self._http: HttpSecurity = None

    def init(self, web_security: WebSecurity):
        http = self._get_http()
        http.set_shared_object(WebSecurity, web_security)
        web_security.add_security_builder(http)

    def configure(self, web_security: WebSecurity):
        pass

    def authentication_manager_bean(self):
        return AuthenticationManagerDelegator(self._authentication_builder)

    @autowired
    def set_authentication_config(self, authentication_configuration: AuthenticationConfiguration):
        self._authentication_configuration = authentication_configuration

    def _configure_authentication(self, auth: AuthenticationManagerBuilder):
        pass

    def _get_http(self) -> HttpSecurity:
        if self._http:
            return self._http
        authentication_manager = self._get_authentication_manager()
        self._authentication_builder.with_parent_authentication_manager(authentication_manager)

        self._http = HttpSecurity(self._authentication_builder)
        self._set_shared_objects_for_http(self._http)
        self._configure_http(self._http)
        return self._http

    def _configure_http(self, http: HttpSecurity):
        http.http_basic()

    def _get_authentication_manager(self) -> AuthenticationManager:
        if not self._authentication_manager_initialized:
            self._configure_authentication(self._local_authentication_builder)
            if self._enable_local_authentication:
                self._authentication_manager = self._local_authentication_builder.build()
            else:
                self._authentication_manager = self._authentication_configuration.authentication_manager
            self._authentication_manager_initialized = True
        return self._authentication_manager

    def _set_shared_objects_for_http(self, http: HttpSecurity):
        for k, v in self._local_authentication_builder.get_shared_objects():
            http.set_shared_object(k, v)


class AuthenticationManagerDelegator(AuthenticationManager):
    def __init__(self, delegate_builder: AuthenticationManagerBuilder):
        self._delegate_builder = delegate_builder
        self._delegate: AuthenticationManager = None

    def authenticate(self, authentication: Authentication) -> Authentication:
        if self._delegate is None:
            self._delegate = self._delegate_builder.object
        return self._delegate.authenticate(authentication)
