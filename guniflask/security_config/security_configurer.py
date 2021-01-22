from typing import Optional

from guniflask.security_config.security_builder import SecurityBuilder


class SecurityConfigurer:
    def __init__(self):
        self._security_builder: Optional[SecurityBuilder] = None

    def init(self, builder: SecurityBuilder):
        pass

    def configure(self, builder: SecurityBuilder):
        pass

    @property
    def builder(self):
        return self._security_builder

    @builder.setter
    def builder(self, value: SecurityBuilder):
        self._security_builder = value
