# coding=utf-8

from abc import ABCMeta, abstractmethod
import datetime as dt

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.combining import AndTrigger
from guniflask.beans.factory_hook import SmartInitializingSingleton, DisposableBean

__all__ = ['TaskScheduler', 'DefaultTaskScheduler']


class TaskScheduler(metaclass=ABCMeta):
    @abstractmethod
    def schedule(self, task, start_time: dt.datetime = None):
        pass

    @abstractmethod
    def schedule_with_cron(self, task, cron: str, start_time: dt.datetime = None):
        pass

    @abstractmethod
    def schedule_with_fixed_interval(self, task, interval: int, start_time: dt.datetime = None):
        pass


class DefaultTaskScheduler(TaskScheduler, SmartInitializingSingleton, DisposableBean):
    def __init__(self, scheduler=None):
        self._scheduler = scheduler or BackgroundScheduler()

    @property
    def scheduler(self):
        return self._scheduler

    def schedule(self, task, start_time: dt.datetime = None):
        trigger = None
        if start_time is not None:
            trigger = DateTrigger(start_time)
        self._scheduler.add_job(task, trigger=trigger)

    def schedule_with_cron(self, task, cron: str, start_time: dt.datetime = None):
        cron_trigger = CronTrigger.from_crontab(cron)
        if start_time is not None:
            trigger = AndTrigger([cron_trigger, DateTrigger(start_time)])
        else:
            trigger = cron_trigger
        self._scheduler.add_job(task, trigger=trigger)

    def schedule_with_fixed_interval(self, task, interval: int, start_time: dt.datetime = None):
        interval_trigger = IntervalTrigger(seconds=interval)
        if start_time is not None:
            trigger = AndTrigger([interval_trigger, DateTrigger(start_time)])
        else:
            trigger = interval_trigger
        self._scheduler.add_job(task, trigger=trigger)

    def start(self):
        self._scheduler.start(paused=False)

    def shutdown(self, wait=True):
        self._scheduler.shutdown(wait=wait)

    def after_singletons_instantiated(self):
        self.start()

    def destroy(self):
        self.shutdown(wait=False)
