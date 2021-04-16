from flask import abort

from guniflask.config.app_settings import settings
from guniflask.context import configuration, bean
from guniflask.web.bind_annotation import blueprint, get_route


@blueprint
class HealthCheckEndpoint:

    @get_route('/health')
    def health_check(self, app_name: str = None):
        if app_name is not None and settings['app_name'] != app_name:
            abort(400, 'APP name not matched')
        return {'status': 'UP'}


@configuration
class HealthCheckConfiguration:
    @bean
    def heath_check_endpoint(self) -> HealthCheckEndpoint:
        endpoint = HealthCheckEndpoint()
        return endpoint
