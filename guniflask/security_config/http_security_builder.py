# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.security_config.configured_security_builder import ConfiguredSecurityBuilder
from guniflask.web.request_filter import RequestFilter

__all__ = ['HttpSecurityBuilder']


class HttpSecurityBuilder(ConfiguredSecurityBuilder, metaclass=ABCMeta):

    @abstractmethod
    def add_request_filter(self, request_filter: RequestFilter):
        pass
