from flask import Flask

from guniflask.beans.definition import BeanDefinition
from guniflask.context.default_bean_context import AnnotationConfigBeanContext
from guniflask.web.blueprint_post_processor import BlueprintPostProcessor
from guniflask.web.config_constants import *


class WebApplicationContext(AnnotationConfigBeanContext):
    def __init__(self, app: Flask):
        super().__init__()
        self.app = app

    def _post_process_bean_factory(self):
        super()._post_process_bean_factory()

        if not self.contains_bean_definition(BLUEPRINT_POST_PROCESSOR):
            bean_definition = BeanDefinition(BlueprintPostProcessor)
            self.register_bean_definition(BLUEPRINT_POST_PROCESSOR, bean_definition)
