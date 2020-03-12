# coding=utf-8

from guniflask.annotation.core import AnnotationMetadata
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.context.condition import ConditionContext
from guniflask.context.annotation import Conditional

__all__ = ['ConditionEvaluator']


class ConditionEvaluator:
    def __init__(self, registry: BeanDefinitionRegistry):
        self.context = ConditionContext(registry)

    def should_skip(self, metadata: AnnotationMetadata):
        if metadata is None or not metadata.is_annotated(Conditional):
            return False
        condition_cls = self.get_condition_class(metadata)
        condition = condition_cls()
        if not condition.matches(self.context, metadata):
            return True
        return False

    def get_condition_class(self, metadata: AnnotationMetadata):
        annotation = metadata.get_annotation(Conditional)
        return annotation['condition']
