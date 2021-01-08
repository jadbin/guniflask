import fcntl
from os.path import join

from guniflask.config.app_settings import settings
from guniflask.utils.path import make_temp_dir


class ServiceLock:
    locks = {}

    def __init__(self, name: str):
        self.name = name

    def acquire(self) -> bool:
        instance_id = self._generate_instance_id()
        if instance_id in self.locks:
            return True

        temp_dir = make_temp_dir(self.__class__.__name__)
        fd = open(join(temp_dir, instance_id), 'w')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            return False
        self.locks[instance_id] = fd
        return True

    def _generate_instance_id(self) -> str:
        return f'{settings["app_name"]}.{settings["port"]}.lock'

    def release(self):
        instance_id = self._generate_instance_id()
        if instance_id in self.locks:
            fd = self.locks.pop(instance_id)
            try:
                fd.close()
            except IOError:
                pass
