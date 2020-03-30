# coding=utf-8

from abc import ABCMeta, abstractmethod
from typing import Any

__all__ = ['SecurityBuilder', 'AbstractSecurityBuilder']


class SecurityBuilder(metaclass=ABCMeta):
    @abstractmethod
    def build(self):
        pass


class AbstractSecurityBuilder(SecurityBuilder, metaclass=ABCMeta):
    def __init__(self):
        self._object: Any = None

    def build(self):
        self._object = self._do_build()
        return self._object

    @property
    def object(self) -> Any:
        return self._object

    @abstractmethod
    def _do_build(self) -> Any:
        pass
