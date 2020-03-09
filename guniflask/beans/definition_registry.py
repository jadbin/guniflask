# coding=utf-8

from typing import List

from guniflask.beans.definition import BeanDefinition
from guniflask.beans.errors import NoSuchBeanDefinitionError, BeanDefinitionStoreError

__all__ = ['BeanDefinitionRegistry']


class BeanDefinitionRegistry:
    def __init__(self):
        self._bean_definition_map = {}
        self._allow_bean_definition_overriding = True

    def set_allow_bean_definition_overriding(self, allow_bean_definition_overriding: bool):
        self._allow_bean_definition_overriding = allow_bean_definition_overriding

    @property
    def is_allow_bean_definition_overriding(self) -> bool:
        return self._allow_bean_definition_overriding

    def register_bean_definition(self, bean_name: str, bean_definition: BeanDefinition):
        old_bean_definition = self._bean_definition_map.get(bean_name)
        if old_bean_definition is not None:
            if not self.is_allow_bean_definition_overriding:
                raise BeanDefinitionStoreError('A bean named "{}" is already bound'.format(bean_name))
        self._bean_definition_map[bean_name] = bean_definition

    def get_bean_definition(self, bean_name: str) -> BeanDefinition:
        bean_definition = self._bean_definition_map.get(bean_name)
        if bean_definition is None:
            raise NoSuchBeanDefinitionError(bean_name)
        return bean_definition

    def get_bean_definition_names(self) -> List[str]:
        return list(self._bean_definition_map.keys())

    def contains_bean_definition(self, bean_name: str) -> bool:
        return bean_name in self._bean_definition_map

    def remove_bean_definition(self, bean_name: str):
        if bean_name not in self._bean_definition_map:
            raise NoSuchBeanDefinitionError(bean_name)
        self._bean_definition_map.pop(bean_name)
