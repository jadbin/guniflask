import datetime as dt
from abc import ABCMeta, abstractmethod

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from guniflask.beans.lifecycle import SmartInitializingSingleton, DisposableBean


class TaskScheduler(metaclass=ABCMeta):
    @abstractmethod
    def schedule(self, task, start_time: dt.datetime = None):
        pass  # pragma: no cover

    @abstractmethod
    def schedule_with_cron(self, task, cron: str, start_time: dt.datetime = None):
        pass  # pragma: no cover

    @abstractmethod
    def schedule_with_fixed_interval(self, task, interval: int, start_time: dt.datetime = None):
        pass  # pragma: no cover


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
        values = cron.split()
        if len(values) != 5:
            raise ValueError(f'Wrong number of fields: got {len(values)}, expected 5')
        cron_trigger = CronTrigger(minute=values[0], hour=values[1], day=values[2], month=values[3],
                                   day_of_week=values[4], start_date=start_time)
        self._scheduler.add_job(task, trigger=cron_trigger)

    def schedule_with_fixed_interval(self, task, interval: int, start_time: dt.datetime = None):
        interval_trigger = IntervalTrigger(seconds=interval, start_date=start_time)
        self._scheduler.add_job(task, trigger=interval_trigger)

    def start(self):
        self._scheduler.start(paused=False)

    def shutdown(self, wait=True):
        self._scheduler.shutdown(wait=wait)

    def after_singletons_instantiated(self):
        self.start()

    def destroy(self):
        self.shutdown(wait=False)
