# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.annotation.core import AnnotationMetadata
from guniflask.beans.factory import BeanFactory
from guniflask.beans.definition_registry import BeanDefinitionRegistry

__all__ = ['ConditionContext', 'Condition']


class ConditionContext:
    def __init__(self, registry: BeanDefinitionRegistry):
        self.registry = registry
        if isinstance(registry, BeanFactory):
            self.bean_factory = registry
        else:
            self.bean_factory = None


class Condition(metaclass=ABCMeta):
    @abstractmethod
    def matches(self, context: ConditionContext, metadata: AnnotationMetadata) -> bool:
        pass
