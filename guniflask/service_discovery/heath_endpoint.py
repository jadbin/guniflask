# coding=utf-8

from flask import abort

from guniflask.web.bind_annotation import blueprint, get_route
from guniflask.config.app_config import settings

__all__ = ['HealthEndpoint']


@blueprint
class HealthEndpoint:

    @get_route('/health')
    def health_check(self, name: str = None, active_profiles: str = None):
        if not self._check_info(name, active_profiles):
            abort(400, 'Active profiles check failed')
        return {'status': 'UP'}

    def _check_info(self, name: str, active_profile: str):
        if name != settings['project_name']:
            return False

        if not active_profile:
            return not settings['active_profiles']

        profiles = set(active_profile.split(','))
        app_profiles = set(settings['active_profiles'] or [])
        if profiles == app_profiles:
            return True

        return False
