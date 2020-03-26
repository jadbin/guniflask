# coding=utf-8

from guniflask.context import configuration
from guniflask.beans import SmartInitializingSingleton
from guniflask.web import CorsConfiguration
from guniflask.config import settings


@configuration
class WebConfiguration(SmartInitializingSingleton):

    def after_singletons_instantiated(self):
        self.configure_cors()

    def configure_cors(self):
        cors = settings.get_by_prefix('guniflask.cors')
        if cors:
            cors_config = CorsConfiguration()
            if isinstance(cors, dict):
                cors_config.set_default_config(**cors)
                resources = cors.get('resources')
                if resources and isinstance(resources, dict):
                    for k, v in resources.items():
                        if isinstance(v, dict):
                            cors_config.add_resource(k, **v)
                        else:
                            cors_config.add_resource(k)
            cors_config.configure()
