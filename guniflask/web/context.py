# coding=utf-8

from flask import Flask

from guniflask.context.default_bean_context import AnnotationConfigBeanContext
from guniflask.web.blueprint_post_processor import BlueprintPostProcessor
from guniflask.security_config.web_security_config import WebSecurityConfiguration
from guniflask.web.scheduling_config import WebAsyncConfiguration, WebSchedulingConfiguration
from guniflask.web.config_constants import *
from guniflask.beans.definition import BeanDefinition
from guniflask.service_discovery.config import ServiceDiscoveryConfiguration

__all__ = ['WebApplicationContext']


class WebApplicationContext(AnnotationConfigBeanContext):
    def __init__(self, app: Flask):
        super().__init__()
        self.app = app

    def _post_process_bean_factory(self):
        super()._post_process_bean_factory()

        if not self.contains_bean_definition(BLUEPRINT_POST_PROCESSOR):
            bean_definition = BeanDefinition(BlueprintPostProcessor)
            self.register_bean_definition(BLUEPRINT_POST_PROCESSOR, bean_definition)

        self._reader.register(WebSecurityConfiguration)
        self._reader.register(WebAsyncConfiguration)
        self._reader.register(WebSchedulingConfiguration)
        self._reader.register(ServiceDiscoveryConfiguration)
