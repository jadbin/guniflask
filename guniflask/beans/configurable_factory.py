# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.beans.factory import BeanFactory
from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.beans.singleton_registry import SingletonBeanRegistry

__all__ = ['ConfigurableBeanFactory']


class ConfigurableBeanFactory(SingletonBeanRegistry, BeanFactory, metaclass=ABCMeta):

    @abstractmethod
    def add_bean_post_processor(self, bean_post_processor: BeanPostProcessor):
        pass

    @abstractmethod
    def pre_instantiate_singletons(self):
        pass
