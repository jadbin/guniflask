# coding=utf-8

from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.beans.definition import BeanDefinition
from guniflask.context.configuration_post_processor import ConfigurationClassPostProcessor
from guniflask.context.annotation_config_constants import *

__all__ = ['AnnotationConfigUtils']


class AnnotationConfigUtils:

    @staticmethod
    def register_annotation_config_processors(registry: BeanDefinitionRegistry):
        if not registry.contains_bean_definition(CONFIGURATION_ANNOTATION_PROCESSOR):
            bean_definition = BeanDefinition(ConfigurationClassPostProcessor)
            registry.register_bean_definition(CONFIGURATION_ANNOTATION_PROCESSOR,
                                              bean_definition)
