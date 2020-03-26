# coding=utf-8

from guniflask.context import configuration
from guniflask.beans import SmartInitializingSingleton
from guniflask.security import JwtManager
from guniflask.config import settings


@configuration
class JwtConfiguration(SmartInitializingSingleton):

    def after_singletons_instantiated(self):
        self.configure_jwt()

    def configure_jwt(self):
        jwt_config = settings.get_by_prefix('guniflask.jwt')
        if jwt_config and isinstance(jwt_config, dict):
            jwt_manager = JwtManager(**jwt_config)
            jwt_manager.configure()
