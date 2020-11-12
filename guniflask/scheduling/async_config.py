from abc import ABCMeta, abstractmethod

from guniflask.context.annotation import configuration, bean
from guniflask.scheduling.async_executor import AsyncExecutor, DefaultAsyncExecutor
from guniflask.scheduling.async_post_processor import AsyncPostProcessor
from guniflask.scheduling.config_constants import *


class AsyncConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def get_async_executor(self) -> AsyncExecutor:
        pass  # pragma: no cover


@configuration
class AsyncConfiguration:
    def __init__(self, async_configurer: AsyncConfigurer = None):
        if async_configurer is None:
            self._async_executor = DefaultAsyncExecutor()
        else:
            self._async_executor = async_configurer.get_async_executor()

    @bean(ASYNC_ANNOTATION_PROCESSOR)
    def async_annotation_processor(self) -> AsyncPostProcessor:
        return AsyncPostProcessor()

    @bean
    def async_executor(self) -> AsyncExecutor:
        return self._async_executor
