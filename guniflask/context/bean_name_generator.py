from guniflask.annotation import AnnotationUtils
from guniflask.beans.definition import BeanDefinition
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.beans.name_generator import DefaultBeanNameGenerator, BeanNameGenerator
from guniflask.context.annotation import Component


class AnnotationBeanNameGenerator(BeanNameGenerator):
    def __init__(self):
        self._default_generator = DefaultBeanNameGenerator()

    def generate_bean_name(self, bean_definition: BeanDefinition,
                           registry: BeanDefinitionRegistry) -> str:
        bean_name = None
        annotations = AnnotationUtils.get_annotations(bean_definition.source)
        for annotation in annotations:
            if isinstance(annotation, Component):
                name = annotation['name']
                if name is not None:
                    if bean_name is not None and name != bean_name:
                        raise ValueError('Annotations suggest inconsistent component names: '
                                         f'"{bean_name}" versus {name}')
                    bean_name = name
        if bean_name is not None:
            return bean_name
        return self._default_generator.generate_bean_name(bean_definition, registry)
