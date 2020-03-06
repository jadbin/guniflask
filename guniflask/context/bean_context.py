# coding=utf-8

from typing import List

from guniflask.beans.factory import BeanFactory
from guniflask.beans.definition_registry import BeanDefinitionRegistry
from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.beans.factory_post_processor import BeanFactoryPostProcessor, BeanDefinitionRegistryPostProcessor
from guniflask.context.annotation_config_registry import AnnotationConfigRegistry
from guniflask.context.annotation_config_registry import AnnotatedBeanDefinitionReader, ModuleBeanDefinitionScanner
from guniflask.context.annotation_config_constants import *

__all__ = ['BeanContext', 'AnnotationConfigBeanContext']


class BeanContext:
    def __init__(self):
        self._bean_factory_post_processors = []

    @property
    def bean_factory(self) -> BeanFactory:
        raise NotImplemented

    def add_bean_factory_post_processor(self, post_processor: BeanFactoryPostProcessor):
        self._bean_factory_post_processors.append(post_processor)

    @property
    def bean_factory_post_processors(self) -> List[BeanFactoryPostProcessor]:
        return self._bean_factory_post_processors

    def refresh(self):
        bean_factory = self.bean_factory
        self._post_process_bean_factory(bean_factory)
        self._invoke_bean_factory_post_processors(bean_factory)
        self._register_bean_post_processors(bean_factory)
        self._finish_bean_factory_initialization(bean_factory)

    def _post_process_bean_factory(self, bean_factory: BeanFactory):
        pass

    def _invoke_bean_factory_post_processors(self, bean_factory: BeanFactory):
        def invoke_bean_factory_post_processors(post_processors, factory):
            for post_processor in post_processors:
                post_processor.post_process_bean_factory(factory)

        def invoke_bean_definition_registry_post_processors(post_processors, registry):
            for post_processor in post_processors:
                post_processor.post_process_bean_definition_registry(registry)

        if isinstance(bean_factory, BeanDefinitionRegistry):
            for post_processor in self.bean_factory_post_processors:
                if isinstance(post_processor, BeanDefinitionRegistryPostProcessor):
                    post_processor.post_process_bean_definition_registry(bean_factory)

        post_processor_beans = list(bean_factory.get_beans_of_type(BeanFactoryPostProcessor).values())
        if isinstance(bean_factory, BeanDefinitionRegistry):
            regular_post_processors = []
            registry_post_processors = []
            for post_processor in (post_processor_beans + self.bean_factory_post_processors):
                if isinstance(post_processor, BeanDefinitionRegistryPostProcessor):
                    registry_post_processors.append(post_processor)
                regular_post_processors.append(post_processor)
            invoke_bean_definition_registry_post_processors(registry_post_processors, bean_factory)
            invoke_bean_factory_post_processors(regular_post_processors, bean_factory)
        else:
            invoke_bean_factory_post_processors(post_processor_beans, bean_factory)
            invoke_bean_factory_post_processors(self.bean_factory_post_processors, bean_factory)

    def _register_bean_post_processors(self, bean_factory: BeanFactory):
        def register_bean_post_processors(factory, post_processors):
            for post_processor in post_processors:
                factory.add_bean_post_processor(post_processor)

        post_processor_beans = bean_factory.get_beans_of_type(BeanPostProcessor)
        register_bean_post_processors(bean_factory, post_processor_beans)

    def _finish_bean_factory_initialization(self, bean_factory: BeanFactory):
        bean_factory.pre_instantiate_singletons()


class AnnotationConfigBeanContext(BeanContext, AnnotationConfigRegistry):
    def __init__(self):
        BeanContext.__init__(self)
        self._bean_factory = BeanFactory()
        self._reader = AnnotatedBeanDefinitionReader(self.bean_factory)
        self._scanner = ModuleBeanDefinitionScanner(self.bean_factory)

    @property
    def bean_factory(self):
        return self._bean_factory

    def register(self, *annotated_elements):
        self._reader.register(*annotated_elements)

    def scan(self, *base_modules):
        self._scanner.scan(*base_modules)

    def set_bean_name_generator(self, bean_name_generator):
        self._reader.set_bean_name_generator(bean_name_generator)
        self._scanner.set_bean_name_generator(bean_name_generator)
        self.bean_factory.register_singleton(CONFIGURATION_BEAN_NAME_GENERATOR, bean_name_generator)
