from flask import abort

from guniflask.config.app_settings import settings
from guniflask.web.bind_annotation import blueprint, get_route


@blueprint
class HealthEndpoint:

    @get_route('/health')
    def health_check(self, app_id: str = None):
        if app_id is not None and settings['app_id'] != app_id:
            abort(400, 'APP ID not matched')
        return {'status': 'UP'}
