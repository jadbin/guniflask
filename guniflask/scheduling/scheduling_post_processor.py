import datetime as dt
import inspect

from guniflask.annotation import AnnotationUtils
from guniflask.beans.factory import BeanFactory, BeanFactoryAware
from guniflask.beans.lifecycle import SmartInitializingSingleton
from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.scheduling.annotation import Scheduled
from guniflask.scheduling.task_scheduler import TaskScheduler


class ScheduledPostProcessor(BeanPostProcessor, BeanFactoryAware, SmartInitializingSingleton):

    def __init__(self, task_scheduler: TaskScheduler = None):
        self.bean_factory = None
        self.task_scheduler = task_scheduler
        self._scheduled_tasks = []

    def set_bean_factory(self, bean_factory: BeanFactory):
        self.bean_factory = bean_factory

    def post_process_after_initialization(self, bean, bean_name: str):
        bean_type = bean.__class__
        for m in dir(bean_type):
            func = getattr(bean_type, m)
            if inspect.isfunction(func):
                a = AnnotationUtils.get_annotation(func, Scheduled)
                if a is not None:
                    method = getattr(bean, m)
                    self._scheduled_tasks.append((a, method))
        return bean

    def after_singletons_instantiated(self):
        self._finish_registration()

    def _finish_registration(self):
        if self.task_scheduler is None:
            assert self.bean_factory is not None and isinstance(self.bean_factory, BeanFactory), \
                'Bean factory must be set to find task scheduler'
            self.task_scheduler = self.bean_factory.get_bean_of_type(TaskScheduler)

        for scheduled, method in self._scheduled_tasks:
            method = self._post_process_scheduled_method(method)
            self._schedule_task(scheduled, method)

    def _schedule_task(self, scheduled: Scheduled, method):
        start_time = None
        if scheduled['initial_delay'] is not None:
            start_time = dt.datetime.now().astimezone() + dt.timedelta(seconds=scheduled['initial_delay'])
        if scheduled['cron'] is not None:
            self.task_scheduler.schedule_with_cron(method, scheduled['cron'], start_time=start_time)
        elif scheduled['interval'] is not None:
            self.task_scheduler.schedule_with_fixed_interval(method, scheduled['interval'], start_time=start_time)
        else:
            self.task_scheduler.schedule(method, start_time=start_time)

    def _post_process_scheduled_method(self, method):
        return method
