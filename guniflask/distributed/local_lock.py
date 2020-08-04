# coding=utf-8

import os
import tempfile
from os.path import join, exists
import fcntl

from guniflask.config.app_config import settings

__all__ = ['ServiceLock']


class ServiceLock:
    locks = {}

    def __init__(self, name: str):
        self.name = name

    def acquire(self) -> bool:
        instance_id = self._generate_instance_id()
        if instance_id in self.locks:
            return True

        temp_dir = join(tempfile.gettempdir(), 'guniflask', self.__class__.__name__)
        if not exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        fd = open(join(temp_dir, instance_id), 'w')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            return False
        self.locks[instance_id] = fd
        return True

    def _generate_instance_id(self) -> str:
        return '{}.{}.lock'.format(settings['project_name'], settings['port'])

    def release(self):
        instance_id = self._generate_instance_id()
        if instance_id in self.locks:
            fd = self.locks.pop(instance_id)
            try:
                fd.close()
            except IOError:
                pass
