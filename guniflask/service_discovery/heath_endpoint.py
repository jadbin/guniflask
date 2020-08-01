# coding=utf-8

from guniflask.web.bind_annotation import blueprint, get_route

__all__ = ['HealthEndpoint']


@blueprint
class HealthEndpoint:

    @get_route('/health')
    def health_check(self):
        return {'status': 'UP'}
