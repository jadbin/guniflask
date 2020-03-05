# coding=utf-8

__all__ = ['BeanDefinition']


class BeanDefinition:
    SCOPE_SINGLETON = 'singleton'
    SCOPE_PROTOTYPE = 'prototype'

    def __init__(self, source):
        self._source = source
        self.scope = self.SCOPE_SINGLETON
        self.factory_bean_name = None

    @property
    def source(self):
        return self._source

    def is_singleton(self) -> bool:
        return self.scope == self.SCOPE_SINGLETON

    def is_prototype(self) -> bool:
        return self.scope == self.SCOPE_PROTOTYPE
