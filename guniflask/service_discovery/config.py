import logging
from abc import ABCMeta, abstractmethod
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from guniflask.config.app_settings import settings, Settings
from guniflask.context.annotation import configuration, bean, condition_on_setting, include
from guniflask.distributed.local_lock import ServiceLock
from guniflask.service_discovery.consul import ConsulClient, ConsulClientError
from guniflask.service_discovery.discovery_client import DiscoveryClient
from guniflask.service_discovery.health_endpoint import HealthEndpoint
from guniflask.service_discovery.load_balancer_client import LoadBalancerClient, RestClient

log = logging.getLogger(__name__)


class ServiceDiscoveryConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def configure(self, service_name: str, app_settings: Settings) -> bool:
        pass  # pragma: no cover

    @property
    @abstractmethod
    def discovery_client(self) -> DiscoveryClient:
        pass  # pragma: no cover

    @property
    @abstractmethod
    def load_balancer_client(self) -> LoadBalancerClient:
        pass  # pragma: no cover


@condition_on_setting('guniflask.consul')
@configuration
class ConsulConfigurer(ServiceDiscoveryConfigurer):

    def __init__(self):
        self._discovery_client: Optional[DiscoveryClient] = None
        self._load_balancer_client: Optional[LoadBalancerClient] = None
        self._register_scheduler = None
        self._service_name: Optional[str] = None

    @property
    def discovery_client(self) -> DiscoveryClient:
        return self._discovery_client

    @property
    def load_balancer_client(self) -> LoadBalancerClient:
        return self._load_balancer_client

    def configure(self, service_name: str, app_settings: Settings):
        config = app_settings.get_by_prefix('guniflask.consul')
        self._service_name = service_name
        self._register_scheduler = BackgroundScheduler()
        self._register_scheduler.start(paused=False)
        self._consul_register(config, app_settings)

    def _consul_register(self, config: dict, app_settings: Settings):
        consul = self._consul_client(config)
        self._discovery_client = consul
        self._load_balancer_client = consul

        job_id = 'consul_register'
        if self._register_scheduler.get_job(job_id) is None:
            self._do_consul_register(consul, app_settings)
            trigger = IntervalTrigger(minutes=1)
            self._register_scheduler.add_job(self._do_consul_register,
                                             args=(consul, app_settings),
                                             id=job_id,
                                             trigger=trigger)

    def _consul_client(self, config: dict) -> ConsulClient:
        client_config = {}
        for i in ['host', 'port', 'dns_port', 'scheme']:
            if i in config:
                client_config[i] = config[i]
        return ConsulClient(**client_config)

    def _do_consul_register(self, consul: ConsulClient, app_settings: Settings):
        local_ip = app_settings['ip_address']
        port = app_settings['port']
        service_id = f'{app_settings["app_name"]}-{local_ip}-{port}'
        heath_url = f'http://{local_ip}:{port}/health?' \
                    f'app_id={app_settings["app_id"]}'
        try:
            consul.register_service(app_settings['app_name'],
                                    service_id=service_id,
                                    address=local_ip,
                                    port=port,
                                    check=consul.http_check(service_id,
                                                            heath_url,
                                                            check_id=service_id,
                                                            interval='10s',
                                                            deregister_after='10m'))
        except ConsulClientError as e:
            log.error('Failed to register service to Consul at %s:%s: %s', consul.host, consul.port, e)


@configuration
@include(ConsulConfigurer)
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

        app_settings = settings._get_current_object()
        service_name = app_settings['app_name']
        if self._service_discovery_configurer is not None:
            self._service_discovery_configurer.configure(service_name, app_settings)
