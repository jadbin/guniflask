# coding=utf-8

from flask import current_app, Flask
from functools import wraps, partial

from guniflask.context.annotation import bean, configuration
from guniflask.scheduling.config_constants import ASYNC_ANNOTATION_PROCESSOR, SCHEDULED_ANNOTATION_PROCESSOR
from guniflask.scheduling.annotation import AsyncRun, Scheduled
from guniflask.scheduling.async_config import AsyncConfiguration
from guniflask.scheduling.async_post_processor import AsyncPostProcessor
from guniflask.scheduling.scheduling_config import SchedulingConfiguration
from guniflask.scheduling.scheduling_post_processor import ScheduledPostProcessor

__all__ = ['WebAsyncConfiguration', 'WebAsyncPostProcessor',
           'WebSchedulingConfiguration', 'WebScheduledPostProcessor']


@configuration
class WebAsyncConfiguration(AsyncConfiguration):

    @bean(ASYNC_ANNOTATION_PROCESSOR)
    def async_annotation_processor(self) -> AsyncPostProcessor:
        return WebAsyncPostProcessor()


class WebAsyncPostProcessor(AsyncPostProcessor):

    def _process_async(self, async_run: AsyncRun, bean, method):
        app = current_app._get_current_object()
        wrapped_method = partial(run_with_app_context, method, app=app)
        wraps(method)(wrapped_method)
        super()._process_async(async_run, bean, wrapped_method)


@configuration
class WebSchedulingConfiguration(SchedulingConfiguration):

    @bean(SCHEDULED_ANNOTATION_PROCESSOR)
    def scheduled_annotation_processor(self) -> ScheduledPostProcessor:
        return WebScheduledPostProcessor()


class WebScheduledPostProcessor(ScheduledPostProcessor):

    def _process_scheduled(self, scheduled: Scheduled, method):
        app = current_app._get_current_object()
        wrapped_method = partial(run_with_app_context, method, app=app)
        wraps(method)(wrapped_method)
        super()._process_scheduled(scheduled, wrapped_method)


def run_with_app_context(func, app: Flask = None):
    if app is not None:
        with app.app_context():
            return func()
    return func()
