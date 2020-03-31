# coding=utf-8

from typing import List
from abc import ABCMeta, abstractmethod

__all__ = ['BeanFactory',
           'BeanNameAware', 'BeanFactoryAware']


class BeanFactory(metaclass=ABCMeta):
    @abstractmethod
    def get_bean(self, bean_name: str, required_type: type = None):
        pass

    @abstractmethod
    def get_bean_of_type(self, required_type: type):
        pass

    @abstractmethod
    def get_beans_of_type(self, required_type: type):
        pass

    @abstractmethod
    def is_type_match(self, bean_name: str, type_to_match: type) -> bool:
        pass

    @abstractmethod
    def get_bean_names_for_type(self, required_type: type) -> List[str]:
        pass


class BeanNameAware(metaclass=ABCMeta):
    @abstractmethod
    def set_bean_name(self, bean_name: str):
        pass


class BeanFactoryAware(metaclass=ABCMeta):
    @abstractmethod
    def set_bean_factory(self, bean_factory: BeanFactory):
        pass
