from guniflask.context.annotation import bean, configuration
from guniflask.scheduling.async_config import AsyncConfiguration
from guniflask.scheduling.async_post_processor import AsyncPostProcessor
from guniflask.scheduling.config_constants import ASYNC_ANNOTATION_PROCESSOR, SCHEDULED_ANNOTATION_PROCESSOR
from guniflask.scheduling.scheduling_config import SchedulingConfiguration
from guniflask.scheduling.scheduling_post_processor import ScheduledPostProcessor
from guniflask.utils.context import run_with_context


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
