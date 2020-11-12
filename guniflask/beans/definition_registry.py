from abc import ABCMeta, abstractmethod
from typing import List

from guniflask.beans.definition import BeanDefinition


class BeanDefinitionRegistry(metaclass=ABCMeta):

    @abstractmethod
    def register_bean_definition(self, bean_name: str, bean_definition: BeanDefinition):
        pass  # pragma: no cover

    @abstractmethod
    def get_bean_definition(self, bean_name: str) -> BeanDefinition:
        pass  # pragma: no cover

    @abstractmethod
    def get_bean_definition_names(self) -> List[str]:
        pass  # pragma: no cover

    @abstractmethod
    def contains_bean_definition(self, bean_name: str) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def remove_bean_definition(self, bean_name: str):
        pass  # pragma: no cover
