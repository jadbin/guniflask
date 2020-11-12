from guniflask.beans.definition import BeanDefinition
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.context.autowired_post_processor import AutowiredAnnotationBeanPostProcessor
from guniflask.context.config_constants import *
from guniflask.context.config_post_processor import ConfigurationClassPostProcessor


class AnnotationConfigUtils:

    @staticmethod
    def register_annotation_config_processors(registry: BeanDefinitionRegistry):
        if not registry.contains_bean_definition(CONFIGURATION_ANNOTATION_PROCESSOR):
            bean_definition = BeanDefinition(ConfigurationClassPostProcessor)
            registry.register_bean_definition(CONFIGURATION_ANNOTATION_PROCESSOR,
                                              bean_definition)
        if not registry.contains_bean_definition(AUTOWIRED_ANNOTATION_PROCESSOR):
            bean_definition = BeanDefinition(AutowiredAnnotationBeanPostProcessor)
            registry.register_bean_definition(AUTOWIRED_ANNOTATION_PROCESSOR,
                                              bean_definition)
