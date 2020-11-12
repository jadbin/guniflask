from abc import ABCMeta, abstractmethod

from apscheduler.schedulers.background import BackgroundScheduler

from guniflask.beans.lifecycle import DisposableBean, SmartInitializingSingleton


class AsyncExecutor(metaclass=ABCMeta):

    @abstractmethod
    def submit(self, task):
        pass  # pragma: no cover


class DefaultAsyncExecutor(AsyncExecutor, SmartInitializingSingleton, DisposableBean):
    def __init__(self, scheduler=None):
        self._scheduler = scheduler or BackgroundScheduler()

    @property
    def scheduler(self):
        return self._scheduler

    def submit(self, task):
        self._scheduler.add_job(task)

    def start(self):
        self._scheduler.start(paused=False)

    def shutdown(self, wait=True):
        self._scheduler.shutdown(wait=wait)

    def after_singletons_instantiated(self):
        self.start()

    def destroy(self):
        self.shutdown(wait=False)
