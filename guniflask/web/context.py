# coding=utf-8

from flask import Flask

from guniflask.context.bean_context import AnnotationConfigBeanContext
from guniflask.web.blueprint_post_processor import BlueprintPostProcessor
from guniflask.web.scheduling_config import WebAsyncConfiguration, WebSchedulingConfiguration

__all__ = ['AnnotationConfigWebApplicationContext']


class AnnotationConfigWebApplicationContext(AnnotationConfigBeanContext):
    def __init__(self, app: Flask):
        super().__init__()
        self.app = app

    def _post_process_bean_factory(self, bean_factory):
        super()._post_process_bean_factory(bean_factory)
        bean_factory.add_bean_post_processor(BlueprintPostProcessor(self.app))
        self._reader.register(WebAsyncConfiguration)
        self._reader.register(WebSchedulingConfiguration)
