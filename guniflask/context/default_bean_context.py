# coding=utf-8

from typing import List
import logging

from guniflask.beans.default_factory import DefaultBeanFactory
from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.beans.factory_post_processor import BeanFactoryPostProcessor, BeanDefinitionRegistryPostProcessor
from guniflask.context.annotation_config_registry import AnnotationConfigRegistry
from guniflask.context.annotation_config_registry import AnnotatedBeanDefinitionReader, ModuleBeanDefinitionScanner
from guniflask.context.config_constants import *
from guniflask.context.event import ApplicationEvent, ContextRefreshedEvent, ContextClosedEvent
from guniflask.context.event_listener import ApplicationEventListener
from guniflask.context.event_publisher import ApplicationEventPublisher
from guniflask.context.context_aware_processor import BeanContextAwareProcessor
from guniflask.context.bean_context import BeanContext

__all__ = ['BeanContext', 'AnnotationConfigBeanContext']

log = logging.getLogger(__name__)


class DefaultBeanContext(DefaultBeanFactory, BeanContext):
    def __init__(self):
        DefaultBeanFactory.__init__(self)
        self._bean_factory_post_processors = []
        self._app_listeners = set()
        self._app_event_publisher = None

    def add_bean_factory_post_processor(self, post_processor: BeanFactoryPostProcessor):
        self._bean_factory_post_processors.append(post_processor)

    @property
    def bean_factory_post_processors(self) -> List[BeanFactoryPostProcessor]:
        return self._bean_factory_post_processors

    def refresh(self):
        self._prepare_bean_factory()
        try:
            self._post_process_bean_factory()
            self._invoke_bean_factory_post_processors()
            self._register_bean_post_processors()
            self._init_application_event_publisher()
            self._register_application_listeners()
            self._finish_bean_factory_initialization()
            self._finish_refresh()
        except Exception:
            log.error('Exception encountered during context initialization', exc_info=True)
            self._destroy_beans()
            raise

    def close(self):
        self.publish_event(ContextClosedEvent(self))
        self._destroy_beans()

    def add_application_listener(self, listener: ApplicationEventListener):
        self._app_listeners.add(listener)

    def publish_event(self, event: ApplicationEvent):
        self._app_event_publisher.publish_event(event)

    def _prepare_bean_factory(self):
        self.add_bean_post_processor(BeanContextAwareProcessor(self))

    def _post_process_bean_factory(self):
        pass

    def _invoke_bean_factory_post_processors(self):
        def invoke_bean_factory_post_processors(post_processors, factory):
            for post_processor in post_processors:
                post_processor.post_process_bean_factory(factory)

        def invoke_bean_definition_registry_post_processors(post_processors, registry):
            for post_processor in post_processors:
                post_processor.post_process_bean_definition_registry(registry)

        for post_processor in self.bean_factory_post_processors:
            if isinstance(post_processor, BeanDefinitionRegistryPostProcessor):
                post_processor.post_process_bean_definition_registry(self)

        post_processor_beans = list(self.get_beans_of_type(BeanFactoryPostProcessor).values())
        regular_post_processors = []
        registry_post_processors = []
        for post_processor in (post_processor_beans + self.bean_factory_post_processors):
            if isinstance(post_processor, BeanDefinitionRegistryPostProcessor):
                registry_post_processors.append(post_processor)
            regular_post_processors.append(post_processor)
        invoke_bean_definition_registry_post_processors(registry_post_processors, self)
        invoke_bean_factory_post_processors(regular_post_processors, self)

    def _register_bean_post_processors(self):
        def register_bean_post_processors(factory, post_processors):
            for post_processor in post_processors:
                factory.add_bean_post_processor(post_processor)

        post_processor_beans = list(self.get_beans_of_type(BeanPostProcessor).values())
        register_bean_post_processors(self, post_processor_beans)

    def _init_application_event_publisher(self):
        self._app_event_publisher = ApplicationEventPublisher(self)
        self.register_singleton(APPLICATION_EVENT_PUBLISHER, self._app_event_publisher)

    def _register_application_listeners(self):
        for listener in self._app_listeners:
            self._app_event_publisher.add_application_listener(listener)
        bean_names = self.get_bean_names_for_type(ApplicationEventListener)
        for bean_name in bean_names:
            self._app_event_publisher.add_application_listener_bean(bean_name)

    def _finish_bean_factory_initialization(self):
        self.pre_instantiate_singletons()

    def _finish_refresh(self):
        self._app_event_publisher.publish_event(ContextRefreshedEvent(self))

    def _destroy_beans(self):
        self.destroy_singletons()


class AnnotationConfigBeanContext(DefaultBeanContext, AnnotationConfigRegistry):
    def __init__(self):
        DefaultBeanContext.__init__(self)
        self._reader = AnnotatedBeanDefinitionReader(self)
        self._scanner = ModuleBeanDefinitionScanner(self)

    def register(self, *annotated_elements):
        self._reader.register(*annotated_elements)

    def scan(self, *base_modules):
        self._scanner.scan(*base_modules)

    def set_bean_name_generator(self, bean_name_generator):
        self._reader.set_bean_name_generator(bean_name_generator)
        self._scanner.set_bean_name_generator(bean_name_generator)
        self.register_singleton(CONFIGURATION_BEAN_NAME_GENERATOR, bean_name_generator)
