# coding=utf-8

from typing import List, get_type_hints
import inspect
from functools import partial
from abc import ABCMeta, abstractmethod

from guniflask.beans.configurable_factory import ConfigurableBeanFactory
from guniflask.beans.definition import BeanDefinition
from guniflask.beans.errors import BeanTypeNotDeclaredError, BeanTypeNotAllowedError, BeanNotOfRequiredTypeError, \
    NoUniqueBeanDefinitionError
from guniflask.beans.post_processor import BeanPostProcessor

__all__ = ['AbstractBeanFactory']


class AbstractBeanFactory(ConfigurableBeanFactory, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self._bean_post_processors = []

    def add_bean_post_processor(self, bean_post_processor: BeanPostProcessor):
        try:
            self._bean_post_processors.remove(bean_post_processor)
        except ValueError:
            pass
        self._bean_post_processors.append(bean_post_processor)

    @property
    def bean_post_processors(self) -> List[BeanPostProcessor]:
        return self._bean_post_processors

    def get_bean(self, bean_name, required_type: type = None):
        bean = None

        share_instance = self.get_singleton(bean_name)
        if share_instance is not None:
            bean = share_instance
        else:
            bean_definition = self.get_bean_definition(bean_name)
            if bean_definition.is_singleton():
                bean = self.get_singleton_from_factory(bean_name,
                                                       partial(self.create_bean, bean_name, bean_definition))
            elif bean_definition.is_prototype():
                # TODO: support prototype
                pass

        # Check if required type matches the type of the actual bean instance.
        if bean is not None and required_type is not None:
            if not issubclass(type(bean), required_type):
                raise BeanNotOfRequiredTypeError(bean, required_type, type(bean))
        return bean

    def get_bean_of_type(self, required_type: type):
        candidates = self.get_beans_of_type(required_type)
        if len(candidates) == 1:
            return list(candidates.values())[0]
        if len(candidates) > 1:
            raise NoUniqueBeanDefinitionError(required_type)

    def get_beans_of_type(self, required_type: type):
        names = self.get_bean_names_for_type(required_type)
        result = {}
        for name in names:
            bean = self.get_bean(name, required_type=required_type)
            result[name] = bean
        return result

    def is_type_match(self, bean_name: str, type_to_match: type) -> bool:
        bean = self.get_singleton(bean_name)
        if bean is not None:
            return isinstance(bean, type_to_match)
        if not self.contains_bean_definition(bean_name):
            return False
        bean_type = self._resolve_bean_type(bean_name, self.get_bean_definition(bean_name))
        if bean_type is None:
            return False
        return issubclass(bean_type, type_to_match)

    def _resolve_bean_type(self, bean_name: str, bean_definition: BeanDefinition) -> type:
        source = bean_definition.source
        if inspect.isclass(source):
            return source
        if inspect.isfunction(source) or inspect.ismethod(source):
            hints = get_type_hints(source)
            if 'return' not in hints:
                raise BeanTypeNotDeclaredError(bean_name)
            bean_type = hints['return']
            if not inspect.isclass(bean_type):
                raise BeanTypeNotAllowedError(bean_name, bean_type)
            return bean_type

    @abstractmethod
    def create_bean(self, bean_name: str, bean_definition: BeanDefinition):
        pass

    @abstractmethod
    def contains_bean_definition(self, bean_name: str) -> bool:
        pass

    @abstractmethod
    def get_bean_definition(self, bean_name: str) -> BeanDefinition:
        pass
