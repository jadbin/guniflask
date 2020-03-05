# coding=utf-8

from abc import abstractmethod, ABCMeta

from guniflask.beans.definition import BeanDefinition
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.beans.errors import BeanDefinitionStoreError
from guniflask.utils.string import string_lowercase_underscore

__all__ = ['BeanNameGenerator', 'DefaultBeanNameGenerator']


class BeanNameGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate_bean_name(self, bean_definition: BeanDefinition,
                           registry: BeanDefinitionRegistry) -> str:
        pass


class DefaultBeanNameGenerator(BeanNameGenerator):

    def generate_bean_name(self, bean_definition: BeanDefinition,
                           bean_definition_registry: BeanDefinitionRegistry) -> str:
        source = bean_definition.source
        if not hasattr(source, '__name__'):
            raise BeanDefinitionStoreError('Cannot generate bean name for : no "__name__" attribute')
        name = source.__name__
        bean_name = string_lowercase_underscore(name)
        return bean_name