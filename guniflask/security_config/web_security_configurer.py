# coding=utf-8

from abc import ABCMeta

from guniflask.security_config.security_configurer import SecurityConfigurer

__all__ = ['WebSecurityConfigurer']


class WebSecurityConfigurer(SecurityConfigurer, metaclass=ABCMeta):
    pass
