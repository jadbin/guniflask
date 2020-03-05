# coding=utf-8

from abc import ABCMeta, abstractmethod
import inspect

from guniflask.beans.definition import BeanDefinition
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.annotation.annotation_utils import AnnotationUtils
from guniflask.context.annotation import Component
from guniflask.context.annotation_config_utils import AnnotationConfigUtils
from guniflask.utils.env import walk_modules
from guniflask.context.bean_name_generator import AnnotationBeanNameGenerator

__all__ = ['AnnotationConfigRegistry',
           'AnnotatedBeanDefinitionReader', 'ModuleBeanDefinitionScanner']


class AnnotationConfigRegistry(metaclass=ABCMeta):
    @abstractmethod
    def register(self, *annotated_elements):
        pass

    @abstractmethod
    def scan(self, *base_modules):
        pass


class AnnotatedBeanDefinitionReader:
    def __init__(self, registry: BeanDefinitionRegistry):
        self._registry = registry
        self._bean_name_generator = AnnotationBeanNameGenerator()
        AnnotationConfigUtils.register_annotation_config_processors(self._registry)

    def register(self, *annotated_elements):
        for e in annotated_elements:
            self.register_bean(e)

    def register_bean(self, annotated_element, name=None):
        bean_definition = BeanDefinition(annotated_element)
        bean_name = name or self._bean_name_generator.generate_bean_name(bean_definition, self._registry)
        self._registry.register_bean_definition(bean_name, bean_definition)

    def set_bean_name_generator(self, bean_name_generator):
        self._bean_name_generator = bean_name_generator


class ModuleBeanDefinitionScanner:
    def __init__(self, registry: BeanDefinitionRegistry):
        self._registry = registry
        self.include_annotation_config = True
        self._bean_name_generator = AnnotationBeanNameGenerator()

    def scan(self, *base_modules):
        self._scan(*base_modules)
        if self.include_annotation_config:
            AnnotationConfigUtils.register_annotation_config_processors(self._registry)

    def set_bean_name_generator(self, bean_name_generator):
        self._bean_name_generator = bean_name_generator

    def _scan(self, *base_modules):
        for base_module in base_modules:
            for module in walk_modules(base_module):
                candidates = self._find_candidate_components(module)
                for bean_definition in candidates:
                    bean_name = self._bean_name_generator.generate_bean_name(bean_definition, self._registry)
                    self._registry.register_bean_definition(bean_name, bean_definition)

    def _find_candidate_components(self, module):
        candidates = []
        for obj in vars(module).values():
            if inspect.isclass(obj) or inspect.isfunction(obj):
                if obj.__module__ == module.__name__:
                    annotation_metadata = AnnotationUtils.get_annotation_metadata(obj)
                    if annotation_metadata is not None and annotation_metadata.is_annotated(Component):
                        bean_definition = BeanDefinition(obj)
                        candidates.append(bean_definition)
        return candidates
