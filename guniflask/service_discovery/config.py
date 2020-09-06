# coding=utf-8

import logging
from abc import ABCMeta, abstractmethod

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from guniflask.config.app_config import settings, Settings
from guniflask.utils.network import get_local_ip_address
from guniflask.service_discovery.consul import ConsulClient, ConsulClientError
from guniflask.distributed.local_lock import ServiceLock
from guniflask.context.annotation import configuration, bean, condition_on_setting
from guniflask.service_discovery.heath_endpoint import HealthEndpoint
from guniflask.service_discovery.discovery_client import DiscoveryClient
from guniflask.service_discovery.load_balancer_client import LoadBalancerClient, LoadBalancedRequest

log = logging.getLogger(__name__)


class ServiceDiscoveryConfigurer(metaclass=ABCMeta):
    @abstractmethod
    def configure(self, service_name: str, app_settings: Settings) -> bool:
        pass

    @property
    @abstractmethod
    def discovery_client(self) -> DiscoveryClient:
        pass

    @property
    @abstractmethod
    def load_balancer_client(self) -> LoadBalancerClient:
        pass


@condition_on_setting('guniflask.consul')
@configuration
class ConsulConfigurer(ServiceDiscoveryConfigurer):

    def __init__(self):
        self._discovery_client: DiscoveryClient = None
        self._load_balancer_client: LoadBalancerClient = None
        self._register_scheduler = None
        self._service_name: str = None

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
        local_ip = get_local_ip_address()
        port = app_settings['port']
        service_id = f'{app_settings["project_name"]}-{local_ip}-{port}'
        heath_url = f'http://{local_ip}:{port}/_health?' \
                    f'name={app_settings["project_name"]}&active_profiles={app_settings["active_profiles"]}'
        try:
            consul.register_service(app_settings['project_name'],
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
class ServiceDiscoveryConfiguration:
    SERVICE_DISCOVERY = {
        'consul': ConsulConfigurer,
    }

    def __init__(self, service_discovery_configurer: ServiceDiscoveryConfigurer = None):
        self._service_discovery_configurer = service_discovery_configurer

        self._register_lock = ServiceLock('service_registration_lock')
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
    def load_balanced_request(self) -> LoadBalancedRequest:
        if self._service_discovery_configurer:
            load_balancer_client = self._service_discovery_configurer.load_balancer_client
            if load_balancer_client is not None:
                return LoadBalancedRequest(load_balancer_client)

    def _auto_register(self):
        if not self._register_lock.acquire():
            return

        app_settings = settings._get_current_object()
        service_name = app_settings['project_name']
        if self._service_discovery_configurer is not None:
            self._service_discovery_configurer.configure(service_name, app_settings)
