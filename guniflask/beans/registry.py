# coding=utf-8

from typing import List

from guniflask.beans.errors import BeanCurrentlyInCreationError

__all__ = ['SingletonBeanRegistry']


class SingletonBeanRegistry:
    def __init__(self):
        self._singleton_objects = {}
        self._singletons_currently_in_creation = set()

    def register_singleton(self, bean_name: str, singleton_obj):
        old_object = self._singleton_objects.get(bean_name)
        if old_object is not None:
            raise ValueError('Cannot register singleton object [{}], '
                             'because the bean name "{}" already exists'.format(singleton_obj, bean_name))
        self._add_singleton(bean_name, singleton_obj)

    def get_singleton(self, bean_name: str):
        return self._singleton_objects.get(bean_name)

    def get_singleton_from_factory(self, bean_name: str, singleton_factory):
        singleton_obj = self._singleton_objects.get(bean_name)
        if singleton_obj is None:
            self._before_singleton_creation(bean_name)
            try:
                singleton_obj = singleton_factory()
            finally:
                self._after_singleton_creation(bean_name)
            if singleton_obj is not None:
                self._add_singleton(bean_name, singleton_obj)
        return singleton_obj

    def contains_singleton(self, bean_name: str) -> bool:
        return bean_name in self._singleton_objects

    def get_singleton_names(self) -> List[str]:
        return list(self._singleton_objects.keys())

    def is_singleton_currently_in_creation(self, bean_name: str) -> bool:
        return bean_name in self._singletons_currently_in_creation

    def _before_singleton_creation(self, bean_name):
        if self.is_singleton_currently_in_creation(bean_name):
            raise BeanCurrentlyInCreationError(bean_name)
        self._singletons_currently_in_creation.add(bean_name)

    def _after_singleton_creation(self, bean_name):
        self._singletons_currently_in_creation.remove(bean_name)

    def _add_singleton(self, bean_name, singleton_obj):
        self._singleton_objects[bean_name] = singleton_obj
