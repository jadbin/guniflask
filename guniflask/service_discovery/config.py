# coding=utf-8

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from guniflask.config.app_config import settings, Settings
from guniflask.utils.network import get_local_ip_address
from guniflask.service_discovery.consul import ConsulClient, ConsulClientError
from guniflask.distributed.local_lock import ServiceLock
from guniflask.context.annotation import configuration, bean
from guniflask.service_discovery.heath_endpoint import HealthEndpoint
from guniflask.service_discovery.discovery_client import DiscoveryClient
from guniflask.service_discovery.load_balancer_client import LoadBalancerClient, LoadBalancedRequest

__all__ = ['ServiceDiscoveryConfiguration']

log = logging.getLogger(__name__)


@configuration
class ServiceDiscoveryConfiguration:
    SERVICE_REGISTRY_NAMES = ['consul']

    def __init__(self):
        self.service_name = settings['project_name']
        self._discovery_client: DiscoveryClient = None
        self._load_balancer_client: LoadBalancerClient = None

        self._register_scheduler = BackgroundScheduler()
        self._register_scheduler.start(paused=False)
        self._register_lock = ServiceLock('service_registration_lock')
        self._auto_register()

    @bean
    def heath_endpoint(self) -> HealthEndpoint:
        endpoint = HealthEndpoint()
        return endpoint

    @bean
    def discovery_client(self) -> DiscoveryClient:
        return self._discovery_client

    @bean
    def load_balancer_client(self) -> LoadBalancerClient:
        return self._load_balancer_client

    @bean
    def load_balanced_request(self) -> LoadBalancedRequest:
        if self._load_balancer_client is not None:
            return LoadBalancedRequest(self._load_balancer_client)

    def _auto_register(self):
        if not self._register_lock.acquire():
            return

        app_settings = settings._get_current_object()
        for name in self.SERVICE_REGISTRY_NAMES:
            config = app_settings.get_by_prefix('guniflask.{}'.format(name))
            if config is not None:
                getattr(self, '_{}_register'.format(name))(config, app_settings)

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
        for i in ['host', 'port', 'dns_port']:
            if i in config:
                client_config[i] = config[i]
        return ConsulClient(**client_config)

    def _do_consul_register(self, consul: ConsulClient, app_settings: Settings):
        local_ip = get_local_ip_address()
        port = app_settings['port']
        service_id = '{}-{}-{}'.format(self.service_name, local_ip, port)
        heath_url = 'http://{}:{}/health?' \
                    'name={}&active_profiles={}'.format(local_ip, port,
                                                        app_settings['project_name'],
                                                        ','.join(app_settings['active_profiles']))
        try:
            consul.register_service(self.service_name,
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
