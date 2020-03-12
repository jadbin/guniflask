# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.context import configuration, bean
from guniflask.scheduling.config_constants import *
from guniflask.scheduling.scheduled_post_processor import ScheduledPostProcessor
from guniflask.scheduling.task_scheduler import TaskScheduler, DefaultTaskScheduler

__all__ = ['ScheduledConfigurer', 'ScheduledConfiguration']


class ScheduledConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def get_task_scheduler(self) -> TaskScheduler:
        pass


@configuration
class ScheduledConfiguration:
    def __init__(self, scheduled_configurer: ScheduledConfigurer = None):
        if scheduled_configurer is None:
            self._task_scheduler = DefaultTaskScheduler()
        else:
            self._task_scheduler = scheduled_configurer.get_task_scheduler()

    @bean(SCHEDULED_ANNOTATION_PROCESSOR)
    def scheduled_annotation_processor(self) -> ScheduledPostProcessor:
        return ScheduledPostProcessor()

    @bean(TASK_SCHEDULER)
    def task_scheduler(self) -> TaskScheduler:
        return self._task_scheduler
