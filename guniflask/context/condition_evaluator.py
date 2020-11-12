from guniflask.annotation import AnnotationMetadata
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.context.annotation import Conditional
from guniflask.context.condition import ConditionContext, Condition


class ConditionEvaluator:
    def __init__(self, registry: BeanDefinitionRegistry):
        self.context = ConditionContext(registry)

    def should_skip(self, metadata: AnnotationMetadata):
        if metadata is None or not metadata.is_annotated(Conditional):
            return False
        condition_cls = self.get_condition_class(metadata)
        if isinstance(condition_cls, Condition):
            condition = condition_cls
        else:
            condition = condition_cls()
        if not condition.matches(self.context, metadata):
            return True
        return False

    def get_condition_class(self, metadata: AnnotationMetadata):
        annotation = metadata.get_annotation(Conditional)
        return annotation['condition']
