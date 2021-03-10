import logging
from abc import ABCMeta, abstractmethod

from guniflask.config import settings
from guniflask.context.annotation import configuration, bean, include
from guniflask.distributed.local_lock import ServiceLock
from guniflask.service_discovery.discovery_client import DiscoveryClient
from guniflask.service_discovery.health_endpoint import HealthEndpoint
from guniflask.service_discovery.load_balancer_client import LoadBalancerClient, RestClient

log = logging.getLogger(__name__)


class ServiceDiscoveryConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def configure(self, service_name: str) -> bool:
        pass  # pragma: no cover

    @property
    @abstractmethod
    def discovery_client(self) -> DiscoveryClient:
        pass  # pragma: no cover

    @property
    @abstractmethod
    def load_balancer_client(self) -> LoadBalancerClient:
        pass  # pragma: no cover


@configuration
@include('guniflask.service_discovery.consul.ConsulConfigurer')
class ServiceDiscoveryConfiguration:

    def __init__(self, service_discovery_configurer: ServiceDiscoveryConfigurer = None):
        self._service_discovery_configurer = service_discovery_configurer

        self._register_lock = ServiceLock('__service_registration_lock')
        self._auto_register()

    @bean
    def heath_endpoint(self) -> HealthEndpoint:
        endpoint = HealthEndpoint()
        return endpoint

    @bean
    def discovery_client(self) -> DiscoveryClient:
        if self._service_discovery_configurer:
            return self._service_discovery_configurer.discovery_client

    @bean
    def load_balancer_client(self) -> LoadBalancerClient:
        if self._service_discovery_configurer:
            return self._service_discovery_configurer.load_balancer_client

    @bean
    def load_balanced_request(self) -> RestClient:
        if self._service_discovery_configurer:
            load_balancer_client = self._service_discovery_configurer.load_balancer_client
            if load_balancer_client is not None:
                return RestClient(load_balancer_client)

    def _auto_register(self):
        if not self._register_lock.acquire():
            return

        service_name = settings['app_name']
        if self._service_discovery_configurer is not None:
            self._service_discovery_configurer.configure(service_name)
