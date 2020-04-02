# coding=utf-8

from typing import List

from guniflask.security.user_details import UserDetails
from guniflask.security.authentication import Authentication
from guniflask.security_config.authentication_manager_builder import AuthenticationManagerBuilder
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security_config.http_security import HttpSecurity
from guniflask.security_config.authentication_config import AuthenticationConfiguration
from guniflask.beans.annotation import autowired
from guniflask.security_config.security_configurer import SecurityConfigurerAdapter
from guniflask.security_config.web_security import WebSecurity
from guniflask.security.user_details_service import UserDetailsService
from guniflask.context.bean_context import BeanContext, BeanContextAware

__all__ = ['WebSecurityConfigurer']


class WebSecurityConfigurer(SecurityConfigurerAdapter, BeanContextAware):
    def __init__(self):
        super().__init__()
        self._authentication_configuration: AuthenticationConfiguration = None
        self._authentication_builder = AuthenticationManagerBuilder()
        self._local_authentication_builder = AuthenticationManagerBuilder()
        self._enable_local_authentication = False
        self._authentication_manager: AuthenticationManager = None
        self._authentication_manager_initialized = False
        self._http: HttpSecurity = None
        self._context: BeanContext = None

    def init(self, web_security: WebSecurity):
        http = self._get_http()
        web_security.add_security_builder(http)

    def configure(self, web_security: WebSecurity):
        pass

    def configure_http(self, http: HttpSecurity):
        pass

    def configure_authentication(self, authentication_builder: AuthenticationManagerBuilder):
        pass

    def authentication_manager_bean(self) -> AuthenticationManager:
        return AuthenticationManagerDelegator(self._authentication_builder)

    def set_bean_context(self, bean_context: BeanContext):
        self._context = bean_context

    @autowired
    def set_authentication_config(self, authentication_configuration: AuthenticationConfiguration):
        self._authentication_configuration = authentication_configuration

    def _get_http(self) -> HttpSecurity:
        if self._http:
            return self._http
        authentication_manager = self._get_authentication_manager()
        self._authentication_builder.with_parent_authentication_manager(authentication_manager)
        shared_objects = self._create_shared_objects()

        self._http = HttpSecurity(self._authentication_builder, shared_objects=shared_objects)
        self.configure_http(self._http)
        return self._http

    def _get_authentication_manager(self) -> AuthenticationManager:
        if not self._authentication_manager_initialized:
            self.configure_authentication(self._local_authentication_builder)
            if self._enable_local_authentication:
                self._authentication_manager = self._local_authentication_builder.build()
            else:
                self._authentication_manager = self._authentication_configuration.authentication_manager
            self._authentication_manager_initialized = True
        return self._authentication_manager

    def _create_shared_objects(self):
        shared_objects = {}
        for k, v in self._local_authentication_builder.get_shared_objects():
            shared_objects[k] = v
        shared_objects[UserDetailsService] = self._get_user_details_service()
        shared_objects[BeanContext] = self._context
        return shared_objects

    def _get_user_details_service(self) -> UserDetailsService:
        global_auth_builder = self._context.get_bean_of_type(AuthenticationManagerBuilder)
        return UserDetailsServiceDelegator([self._local_authentication_builder, global_auth_builder])


class UserDetailsServiceDelegator(UserDetailsService):
    def __init__(self, delegate_builders: List[AuthenticationManagerBuilder]):
        self._delegate_builders = delegate_builders
        self._delegate: UserDetailsService = None

    def load_user_by_username(self, username: str) -> UserDetails:
        if self._delegate is None:
            for builder in self._delegate_builders:
                self._delegate = builder.default_user_details_service
                if self._delegate:
                    break
            if self._delegate is None:
                raise ValueError('User details service is required')
            self._delegate_builders = None

        return self._delegate.load_user_by_username(username)


class AuthenticationManagerDelegator(AuthenticationManager):
    def __init__(self, delegate_builder: AuthenticationManagerBuilder):
        self._delegate_builder = delegate_builder
        self._delegate: AuthenticationManager = None

    def authenticate(self, authentication: Authentication) -> Authentication:
        if self._delegate is None:
            self._delegate = self._delegate_builder.object
            self._delegate_builder = None
        return self._delegate.authenticate(authentication)
