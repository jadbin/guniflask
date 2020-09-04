# coding=utf-8

from typing import List

from guniflask.context.annotation import configuration
from guniflask.beans.lifecycle import SmartInitializingSingleton
from guniflask.security_config.web_security_configurer import WebSecurityConfigurer
from guniflask.security_config.web_security import WebSecurity


@configuration
class WebSecurityConfiguration(SmartInitializingSingleton):
    def __init__(self, configurers: List[WebSecurityConfigurer] = None):
        self.web_security = WebSecurity()
        if configurers:
            for c in configurers:
                self.web_security.apply(c)

    def after_singletons_instantiated(self):
        self.web_security.build()
