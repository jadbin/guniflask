from flask import abort

from guniflask.config.app_settings import settings
from guniflask.web.bind_annotation import blueprint, get_route


@blueprint
class HealthEndpoint:

    @get_route('/health')
    def health_check(self, app_name: str = None):
        if app_name is not None and settings['app_name'] != app_name:
            abort(400, 'APP name not matched')
        return {'status': 'UP'}
