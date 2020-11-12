from typing import List

from guniflask.security_config.configured_security_builder import ConfiguredSecurityBuilder
from guniflask.security_config.security_builder import SecurityBuilder


class WebSecurity(ConfiguredSecurityBuilder):
    def __init__(self):
        super().__init__()
        self._security_builders: List[SecurityBuilder] = []

    def _perform_build(self):
        for builder in self._security_builders:
            builder.build()

    def add_security_builder(self, security_builder: SecurityBuilder):
        self._security_builders.append(security_builder)
