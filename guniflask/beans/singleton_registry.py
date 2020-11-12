import logging
from typing import List

from guniflask.beans.errors import BeanCurrentlyInCreationError
from guniflask.beans.lifecycle import DisposableBean

log = logging.getLogger(__name__)


class SingletonBeanRegistry:
    def __init__(self):
        self._singleton_objects = {}
        self._singletons_currently_in_creation = set()
        self._disposable_beans = {}

    def register_singleton(self, bean_name: str, singleton_obj):
        old_object = self._singleton_objects.get(bean_name)
        if old_object is not None:
            raise ValueError(f'Cannot register singleton object [{singleton_obj}], '
                             f'because the bean name "{bean_name}" already exists')
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

    def register_disposable_bean(self, bean_name: str, bean):
        self._disposable_beans[bean_name] = bean

    def destroy_singletons(self):
        disposable_bean_names = list(self._disposable_beans.keys())
        for bean_name in disposable_bean_names:
            self.destroy_singleton(bean_name)

    def destroy_singleton(self, bean_name: str):
        self._remove_singleton(bean_name)
        if bean_name in self._disposable_beans:
            bean = self._disposable_beans.pop(bean_name)
            self._destroy_bean(bean_name, bean)

    def _before_singleton_creation(self, bean_name):
        if self.is_singleton_currently_in_creation(bean_name):
            raise BeanCurrentlyInCreationError(bean_name)
        self._singletons_currently_in_creation.add(bean_name)

    def _after_singleton_creation(self, bean_name):
        self._singletons_currently_in_creation.remove(bean_name)

    def _add_singleton(self, bean_name, singleton_obj):
        self._singleton_objects[bean_name] = singleton_obj

    def _remove_singleton(self, bean_name):
        if bean_name in self._singleton_objects:
            self._singleton_objects.pop(bean_name)

    def _destroy_bean(self, bean_name, bean: DisposableBean):
        try:
            bean.destroy()
        except Exception:
            log.error(f'Failed to destroy the bean named "{bean_name}"', exc_info=True)
