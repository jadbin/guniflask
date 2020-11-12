import inspect
from abc import ABCMeta, abstractmethod

from guniflask.annotation import AnnotationMetadata, AnnotationUtils
from guniflask.beans.definition import BeanDefinition
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.context.annotation import Component
from guniflask.context.annotation_config_utils import AnnotationConfigUtils
from guniflask.context.bean_name_generator import AnnotationBeanNameGenerator
from guniflask.context.condition_evaluator import ConditionEvaluator
from guniflask.utils.path import walk_modules


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
        self._condition_evaluator = ConditionEvaluator(registry)
        AnnotationConfigUtils.register_annotation_config_processors(self._registry)

    def register(self, *annotated_elements):
        for e in annotated_elements:
            self.register_bean(e)

    def register_bean(self, annotated_element, name=None):
        if self._condition_evaluator.should_skip(AnnotationUtils.get_annotation_metadata(annotated_element)):
            return
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
        self._condition_evaluator = ConditionEvaluator(registry)

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
        selected_id = set()
        for obj in vars(module).values():
            if inspect.isclass(obj) or inspect.isfunction(obj):
                if obj.__module__ == module.__name__:
                    annotation_metadata = AnnotationUtils.get_annotation_metadata(obj)
                    if annotation_metadata is not None and self._is_candidate_component(annotation_metadata):
                        obj_id = id(obj)
                        if obj_id not in selected_id:
                            selected_id.add(obj_id)
                            bean_definition = BeanDefinition(obj)
                            candidates.append(bean_definition)
        return candidates

    def _is_candidate_component(self, metadata: AnnotationMetadata):
        return metadata.is_annotated(Component) and not self._condition_evaluator.should_skip(metadata)
