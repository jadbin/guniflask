# coding=utf-8

from typing import List
from abc import ABCMeta, abstractmethod

from guniflask.beans.definition import BeanDefinition

__all__ = ['BeanDefinitionRegistry']


class BeanDefinitionRegistry(metaclass=ABCMeta):

    @abstractmethod
    def register_bean_definition(self, bean_name: str, bean_definition: BeanDefinition):
        pass

    @abstractmethod
    def get_bean_definition(self, bean_name: str) -> BeanDefinition:
        pass

    @abstractmethod
    def get_bean_definition_names(self) -> List[str]:
        pass

    @abstractmethod
    def contains_bean_definition(self, bean_name: str) -> bool:
        pass

    @abstractmethod
    def remove_bean_definition(self, bean_name: str):
        pass
