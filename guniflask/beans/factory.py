from abc import ABCMeta, abstractmethod
from typing import List

from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.beans.singleton_registry import SingletonBeanRegistry


class BeanFactory(metaclass=ABCMeta):
    @abstractmethod
    def get_bean(self, bean_name: str, required_type: type = None):
        pass  # pragma: no cover

    @abstractmethod
    def get_bean_of_type(self, required_type: type):
        pass  # pragma: no cover

    @abstractmethod
    def get_beans_of_type(self, required_type: type):
        pass  # pragma: no cover

    @abstractmethod
    def is_type_match(self, bean_name: str, type_to_match: type) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def get_bean_names_for_type(self, required_type: type) -> List[str]:
        pass  # pragma: no cover


class BeanNameAware(metaclass=ABCMeta):
    @abstractmethod
    def set_bean_name(self, bean_name: str):
        pass  # pragma: no cover


class BeanFactoryAware(metaclass=ABCMeta):
    @abstractmethod
    def set_bean_factory(self, bean_factory: BeanFactory):
        pass  # pragma: no cover


class ConfigurableBeanFactory(SingletonBeanRegistry, BeanFactory, metaclass=ABCMeta):

    @abstractmethod
    def add_bean_post_processor(self, bean_post_processor: BeanPostProcessor):
        pass  # pragma: no cover

    @abstractmethod
    def pre_instantiate_singletons(self):
        pass  # pragma: no cover
