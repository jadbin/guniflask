# coding=utf-8

import logging
from functools import partial, update_wrapper

from guniflask.annotation.core import AnnotationUtils
from guniflask.beans.post_processor import BeanPostProcessorAdapter
from guniflask.beans.factory import BeanFactory, BeanFactoryAware
from guniflask.beans.factory_hook import SmartInitializingSingleton
from guniflask.scheduling.async_executor import AsyncExecutor
from guniflask.scheduling.annotation import AsyncRun

__all__ = ['AsyncPostProcessor']

log = logging.getLogger(__name__)


class AsyncPostProcessor(BeanPostProcessorAdapter, BeanFactoryAware, SmartInitializingSingleton):

    def __init__(self):
        self.bean_factory = None
        self._async_methods = []

    def set_bean_factory(self, bean_factory: BeanFactory):
        self.bean_factory = bean_factory

    def post_process_after_initialization(self, bean, bean_name: str):
        for m in dir(bean):
            method = getattr(bean, m)
            a = AnnotationUtils.get_annotation(method, AsyncRun)
            if a is not None:
                self._async_methods.append((a, bean, method))
        return bean

    def after_singletons_instantiated(self):
        self._finish_registration()

    def _finish_registration(self):
        assert self.bean_factory is not None and isinstance(self.bean_factory, BeanFactory), \
            'Bean factory must be set to find async executors'
        for async_run, bean, method in self._async_methods:
            self._process_async(async_run, bean, method)

    def _process_async(self, async_run: AsyncRun, bean, method):
        if async_run['executor'] is None:
            async_executor = self.bean_factory.get_bean_of_type(AsyncExecutor)
        else:
            async_executor = self.bean_factory.get_bean(async_run['executor'], required_type=AsyncExecutor)
            if async_executor is None:
                log.error('Cannot find the async executor named "%s"', async_run['executor'])
        if async_executor is not None:
            method_name = method.__name__
            wrapped_method = self.wrap_async_func(method, async_executor)
            setattr(bean, method_name, wrapped_method)

    def wrap_async_func(self, func, async_executor):
        def wrapper(*args, **kwargs):
            wrapped_func = self._post_process_async_method(func)
            task = partial(wrapped_func, *args, **kwargs)
            async_executor.submit(task)

        return update_wrapper(wrapper, func)

    def _post_process_async_method(self, method):
        return method
