# coding=utf-8

from guniflask.context.annotation import configuration, bean
from guniflask.service_discovery.heath_endpoint import HealthEndpoint

__all__ = ['HealthCheckConfiguration']


@configuration
class HealthCheckConfiguration:

    @bean
    def heath_endpoint(self) -> HealthEndpoint:
        endpoint = HealthEndpoint()
        return endpoint
