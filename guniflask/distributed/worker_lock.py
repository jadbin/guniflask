# coding=utf-8

import os
import tempfile
from os.path import join, exists
import fcntl

from guniflask.utils.process import get_master_pid

__all__ = ['MasterWorkerLock']


class MasterWorkerLock:
    worker_locks = {}

    def acquire(self, name: str) -> bool:
        singleton_id = self._generate_singleton_id(name)
        if singleton_id in self.worker_locks:
            return True

        temp_dir = join(tempfile.gettempdir(), 'guniflask', self.__class__.__name__)
        if not exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        fd = open(join(temp_dir, singleton_id), 'w')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            return False
        self.worker_locks[singleton_id] = fd
        return True

    def _generate_singleton_id(self, name: str) -> str:
        master_pid = get_master_pid()
        return '{}.{}.lock'.format(master_pid, name)

    def release(self, name: str):
        singleton_id = self._generate_singleton_id(name)
        if singleton_id in self.worker_locks:
            fd = self.worker_locks.pop(singleton_id)
            try:
                fd.close()
            except IOError:
                pass
