# coding=utf-8

import os
import tempfile
from os.path import join, exists
import fcntl

from guniflask.annotation.core import AnnotationMetadata
from guniflask.context.annotation import conditional
from guniflask.context.condition import Condition, ConditionContext
from guniflask.utils.process import get_master_pid

__all__ = ['global_singleton']


class GlobalSingletonCondition(Condition):
    global_singleton_conditions = {}

    def matches(self, context: ConditionContext, metadata: AnnotationMetadata) -> bool:
        singleton_id = self.generate_singleton_id(metadata)
        if singleton_id in self.global_singleton_conditions:
            return True

        temp_dir = join(tempfile.gettempdir(), 'guniflask', 'global_singleton_lock')
        if not exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        fd = open(join(temp_dir, singleton_id), 'w')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            return False
        self.global_singleton_conditions[singleton_id] = fd
        return True

    def generate_singleton_id(self, metadata: AnnotationMetadata) -> str:
        obj = metadata.source
        if hasattr(obj, '__module__'):
            module_name = obj.__module__
        else:
            module_name = None
        if hasattr(obj, '__name__'):
            obj_name = obj.__name__
        else:
            obj_name = None
        master_pid = get_master_pid()
        return '{}.{}_{}'.format(module_name, obj_name, master_pid)


def global_singleton(func):
    return conditional(GlobalSingletonCondition)(func)
