# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.security_config.security_builder import SecurityBuilder

__all__ = ['SecurityConfigurer', 'SecurityConfigurerAdapter']


class SecurityConfigurer(metaclass=ABCMeta):

    @abstractmethod
    def init(self, builder: SecurityBuilder):
        pass

    @abstractmethod
    def configure(self, builder: SecurityBuilder):
        pass


class SecurityConfigurerAdapter(SecurityConfigurer, metaclass=ABCMeta):

    def __init__(self):
        self._security_builder: SecurityBuilder = None

    def init(self, builder: SecurityBuilder):
        pass

    def configure(self, builder: SecurityBuilder):
        pass

    @property
    def builder(self):
        return self._security_builder

    @builder.setter
    def builder(self, value: SecurityBuilder):
        self._security_builder = value
