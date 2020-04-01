# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.security_config.security_configurer import SecurityConfigurerAdapter
from guniflask.security.user_details_service import UserDetailsService

__all__ = ['UserDetailsAwareConfigurer']


class UserDetailsAwareConfigurer(SecurityConfigurerAdapter, metaclass=ABCMeta):
    @property
    @abstractmethod
    def user_details_service(self) -> UserDetailsService:
        pass
