# coding=utf-8

import inspect

from guniflask.annotation.core import Annotation, AnnotationUtils

__all__ = ['AsyncRun', 'async_run', 'Scheduled', 'scheduled']


class AsyncRun(Annotation):
    def __init__(self, executor: str = None):
        super().__init__(executor=executor)


def async_run(executor: str = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, AsyncRun(executor=executor))
        return func

    if inspect.isclass(executor) or inspect.isfunction(executor):
        f = executor
        executor = None
        return wrap_func(f)
    return wrap_func


class Scheduled(Annotation):
    def __init__(self, cron: str = None, interval: int = None, initial_delay: int = None):
        super().__init__(cron=cron, interval=interval, initial_delay=initial_delay)


def scheduled(cron: str = None, interval: int = None, initial_delay: int = None):
    def wrap_func(func):
        AnnotationUtils.add_annotation(func, Scheduled(cron=cron,
                                                       interval=interval,
                                                       initial_delay=initial_delay))
        return func

    if inspect.isclass(cron) or inspect.isfunction(cron):
        f = cron
        cron = None
        return wrap_func(f)
    return wrap_func
