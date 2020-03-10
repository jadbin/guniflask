# coding=utf-8

import inspect

from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.beans.factory_post_processor import BeanDefinitionRegistryPostProcessor
from guniflask.context.bean_name_generator import AnnotationBeanNameGenerator
from guniflask.beans.registry import SingletonBeanRegistry
from guniflask.annotation.annotation_utils import AnnotationUtils
from guniflask.beans.definition import BeanDefinition
from guniflask.context.annotation import Bean, Component, Configuration
from guniflask.annotation.core import AnnotationMetadata
from guniflask.context.config_constants import *

__all__ = ['ConfigurationClassPostProcessor']


class ConfigurationClassPostProcessor(BeanDefinitionRegistryPostProcessor):

    def __init__(self):
        self._component_bean_name_generator = AnnotationBeanNameGenerator()

    def post_process_bean_definition_registry(self, registry: BeanDefinitionRegistry):
        self._process_config_bean_definitions(registry)

    def _process_config_bean_definitions(self, registry: BeanDefinitionRegistry):
        if isinstance(registry, SingletonBeanRegistry):
            singleton_registry = registry
            if singleton_registry.contains_singleton(CONFIGURATION_BEAN_NAME_GENERATOR):
                generator = singleton_registry.get_singleton(CONFIGURATION_BEAN_NAME_GENERATOR)
                self._component_bean_name_generator = generator

        candidate_names = registry.get_bean_definition_names()
        candidates = {}
        for name in candidate_names:
            bean_definition = registry.get_bean_definition(name)
            if self._is_configuration_class_candidate(bean_definition):
                candidates[name] = bean_definition

        reader = ConfigurationClassBeanDefinitionReader(registry)
        while len(candidates) > 0:
            for bean_name, bean_definition in candidates.items():
                reader.load_bean_definitions(bean_name, bean_definition)

            candidates = {}
            new_candidate_names = registry.get_bean_definition_names()
            if len(new_candidate_names) > len(candidate_names):
                old_candidate_names = set(candidate_names)
                for name in new_candidate_names:
                    if name not in old_candidate_names:
                        bean_definition = registry.get_bean_definition(name)
                        if self._is_configuration_class_candidate(bean_definition):
                            candidates[name] = bean_definition
                candidate_names = new_candidate_names

    def _is_configuration_class_candidate(self, bean_definition: BeanDefinition):
        annotation_metadata = AnnotationUtils.get_annotation_metadata(bean_definition.source)
        if annotation_metadata is None:
            return False
        if annotation_metadata.is_annotated(Configuration):
            return True
        if annotation_metadata.is_annotated(Component):
            return True
        return False


class ConfigurationClassBeanDefinitionReader:
    def __init__(self, registry: BeanDefinitionRegistry):
        self._registry = registry

    def load_bean_definitions(self, bean_name: str, bean_definition: BeanDefinition):
        source = bean_definition.source
        for m in dir(source):
            method = getattr(source, m)
            if inspect.isfunction(method) or inspect.ismethod(method):
                method_metadata = AnnotationUtils.get_annotation_metadata(method)
                if method_metadata is not None and method_metadata.is_annotated(Bean):
                    self._load_bean_definition_for_bean_method(bean_name, method)

    def _load_bean_definition_for_bean_method(self, factory_bean_name: str, method_metadata: AnnotationMetadata):
        method = method_metadata.source
        method_name = method.__name__
        bean_definition = BeanDefinition(method)
        bean_definition.factory_bean_name = factory_bean_name
        attributes = method_metadata.get_annotation(Bean).attributes
        bean_name = attributes.get('name') or method_name
        self._registry.register_bean_definition(bean_name, bean_definition)
