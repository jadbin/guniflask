# coding=utf-8

from abc import ABCMeta, abstractmethod
from typing import Any

__all__ = ['BeanPostProcessor', 'BeanPostProcessorAdapter']


class BeanPostProcessor(metaclass=ABCMeta):
    @abstractmethod
    def post_process_before_instantiation(self, bean_type: type, bean_name: str):
        pass

    @abstractmethod
    def post_process_before_initialization(self, bean: Any, bean_name: str) -> Any:
        pass

    @abstractmethod
    def post_process_after_initialization(self, bean: Any, bean_name: str) -> Any:
        pass


class BeanPostProcessorAdapter(BeanPostProcessor):
    def post_process_before_instantiation(self, bean_type: type, bean_name: str):
        return None

    def post_process_before_initialization(self, bean, bean_name: str):
        return bean

    def post_process_after_initialization(self, bean, bean_name: str):
        return bean
