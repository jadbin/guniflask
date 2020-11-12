from flask import abort

from guniflask.config.app_settings import settings
from guniflask.web.bind_annotation import blueprint, get_route


@blueprint
class HealthEndpoint:

    @get_route('/health')
    def health_check(self):
        return {'status': 'UP'}

    @get_route('/_health')
    def internal_health_check(self, name: str = None, active_profiles: str = None):
        if not self._check_info(name, active_profiles):
            abort(400, 'Signature check failed')
        return self.health_check()

    def _check_info(self, name: str, active_profile: str):
        if name != settings['app_name']:
            return False

        if not active_profile:
            return not settings['active_profiles']

        profiles = active_profile.split(',')
        app_profiles = settings['active_profiles'] or []
        if profiles == app_profiles:
            return True

        return False
