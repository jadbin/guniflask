# coding=utf-8

import inspect

from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.beans.factory_post_processor import BeanDefinitionRegistryPostProcessor
from guniflask.beans.name_generator import BeanNameGenerator
from guniflask.context.bean_name_generator import AnnotationBeanNameGenerator
from guniflask.beans.singleton_registry import SingletonBeanRegistry
from guniflask.beans.definition import BeanDefinition
from guniflask.context.annotation import Bean, Component, Configuration, Include
from guniflask.annotation.core import AnnotationMetadata, AnnotationUtils
from guniflask.context.config_constants import *
from guniflask.context.condition_evaluator import ConditionEvaluator

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

        reader = ConfigurationClassBeanDefinitionReader(registry, self._component_bean_name_generator)
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
        if annotation_metadata.is_annotated(Include):
            return True
        return False


class ConfigurationClassBeanDefinitionReader:
    def __init__(self, registry: BeanDefinitionRegistry, include_bean_name_generator: BeanNameGenerator):
        self._registry = registry
        self._condition_evaluator = ConditionEvaluator(registry)
        self._include_bean_name_generator = include_bean_name_generator

    def load_bean_definitions(self, bean_name: str, bean_definition: BeanDefinition):
        source = bean_definition.source
        meta_data = AnnotationUtils.get_annotation_metadata(source)
        if meta_data.is_annotated(Include):
            self._load_bean_definition_for_included_config(meta_data)
        for m in dir(source):
            method = getattr(source, m)
            if inspect.isfunction(method) or inspect.ismethod(method):
                method_metadata = AnnotationUtils.get_annotation_metadata(method)
                if method_metadata is not None and method_metadata.is_annotated(Bean):
                    self._load_bean_definition_for_bean_method(bean_name, method_metadata)

    def _load_bean_definition_for_bean_method(self, factory_bean_name: str, method_metadata: AnnotationMetadata):
        if self._condition_evaluator.should_skip(method_metadata):
            return
        method = method_metadata.source
        method_name = method.__name__
        bean_definition = BeanDefinition(method)
        bean_definition.factory_bean_name = factory_bean_name
        attributes = method_metadata.get_annotation(Bean).attributes
        bean_name = attributes.get('name') or method_name
        self._registry.register_bean_definition(bean_name, bean_definition)

    def _load_bean_definition_for_included_config(self, metadata: AnnotationMetadata):
        annotation = metadata.get_annotation(Include)
        config_set = annotation['values']
        if config_set:
            for config_cls in config_set:
                config_cls_metadata = AnnotationUtils.get_annotation_metadata(config_cls)
                if self._condition_evaluator.should_skip(config_cls_metadata):
                    continue
                bean_definition = BeanDefinition(config_cls)
                bean_name = self._include_bean_name_generator.generate_bean_name(bean_definition, self._registry)
                self._registry.register_bean_definition(bean_name, bean_definition)
