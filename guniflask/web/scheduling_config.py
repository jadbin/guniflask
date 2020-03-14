# coding=utf-8

from functools import update_wrapper

from flask import current_app, _request_ctx_stack, copy_current_request_context

from guniflask.context.annotation import bean, configuration
from guniflask.scheduling.config_constants import ASYNC_ANNOTATION_PROCESSOR, SCHEDULED_ANNOTATION_PROCESSOR
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

    def _post_process_async_method(self, method):
        wrapped_method = run_with_context(method)
        return super()._post_process_async_method(wrapped_method)


@configuration
class WebSchedulingConfiguration(SchedulingConfiguration):

    @bean(SCHEDULED_ANNOTATION_PROCESSOR)
    def scheduled_annotation_processor(self) -> ScheduledPostProcessor:
        return WebScheduledPostProcessor()


class WebScheduledPostProcessor(ScheduledPostProcessor):

    def _post_process_scheduled_method(self, method):
        wrapped_method = run_with_context(method)
        return super()._post_process_scheduled_method(wrapped_method)


def run_with_context(func):
    if _request_ctx_stack.top is not None:
        func = copy_current_request_context(func)
    app = current_app._get_current_object()

    def wrapper(*args, **kwargs):
        if app is not None:
            with app.app_context():
                return func(*args, **kwargs)
        return func(*args, **kwargs)

    return update_wrapper(wrapper, func)
