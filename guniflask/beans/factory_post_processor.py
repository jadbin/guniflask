# coding=utf-8

from guniflask.beans.factory import ConfigurableBeanFactory
from guniflask.beans.definition_registry import BeanDefinitionRegistry

__all__ = ['BeanFactoryPostProcessor', 'BeanDefinitionRegistryPostProcessor']


class BeanFactoryPostProcessor:
    def post_process_bean_factory(self, bean_factory: ConfigurableBeanFactory):
        pass


class BeanDefinitionRegistryPostProcessor(BeanFactoryPostProcessor):
    def post_process_bean_definition_registry(self, registry: BeanDefinitionRegistry):
        pass
