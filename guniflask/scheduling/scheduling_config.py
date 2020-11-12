from abc import ABCMeta, abstractmethod

from guniflask.context.annotation import configuration, bean
from guniflask.scheduling.config_constants import *
from guniflask.scheduling.scheduling_post_processor import ScheduledPostProcessor
from guniflask.scheduling.task_scheduler import TaskScheduler, DefaultTaskScheduler


class SchedulingConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def get_task_scheduler(self) -> TaskScheduler:
        pass  # pragma: no cover


@configuration
class SchedulingConfiguration:
    def __init__(self, scheduled_configurer: SchedulingConfigurer = None):
        if scheduled_configurer is None:
            self._task_scheduler = DefaultTaskScheduler()
        else:
            self._task_scheduler = scheduled_configurer.get_task_scheduler()

    @bean(SCHEDULED_ANNOTATION_PROCESSOR)
    def scheduled_annotation_processor(self) -> ScheduledPostProcessor:
        return ScheduledPostProcessor()

    @bean
    def task_scheduler(self) -> TaskScheduler:
        return self._task_scheduler
