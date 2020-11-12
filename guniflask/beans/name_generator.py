from abc import abstractmethod, ABCMeta

from guniflask.beans.definition import BeanDefinition
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.utils.string import string_lowercase_underscore


class BeanNameGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate_bean_name(self, bean_definition: BeanDefinition,
                           registry: BeanDefinitionRegistry) -> str:
        pass  # pragma: no cover


class DefaultBeanNameGenerator(BeanNameGenerator):

    def generate_bean_name(self, bean_definition: BeanDefinition,
                           bean_definition_registry: BeanDefinitionRegistry) -> str:
        source = bean_definition.source
        name = source.__name__
        bean_name = string_lowercase_underscore(name)
        return bean_name
