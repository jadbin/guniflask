# coding=utf-8

from abc import ABCMeta, abstractmethod

__all__ = ['InitializingBean', 'SmartInitializingSingleton', 'DisposableBean']


class InitializingBean(metaclass=ABCMeta):
    @abstractmethod
    def after_properties_set(self):
        pass


class SmartInitializingSingleton(metaclass=ABCMeta):
    @abstractmethod
    def after_singletons_instantiated(self):
        pass


class DisposableBean(metaclass=ABCMeta):
    @abstractmethod
    def destroy(self):
        pass
