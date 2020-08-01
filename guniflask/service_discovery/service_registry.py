# coding=utf-8

from threading import Thread
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from guniflask.config.app_config import Settings
from guniflask.utils.network import get_local_ip_address
from guniflask.service_discovery.consul import ConsulClient, ConsulClientError
from guniflask.distributed.local_lock import MasterLevelLock

__all__ = ['ServiceRegistry']

log = logging.getLogger(__name__)


class ServiceRegistry:
    available_registry_names = ['consul']

    def __init__(self, name: str):
        self.service_name = name
        self.consul_register_thread: Thread = None
        self._registry_scheduler = BackgroundScheduler()
        self._registry_scheduler.start(paused=False)
        self._registry_lock = MasterLevelLock(self.__class__.__name__)

    def auto_register(self, app_settings: Settings):
        if not self._registry_lock.acquire():
            return

        for name in self.available_registry_names:
            getattr(self, '_{}_register'.format(name))(app_settings)

    def _consul_register(self, app_settings: Settings):
        config = app_settings.get_by_prefix('guniflask.consul')
        if config is None:
            return

        job_id = 'consul_register'
        if self._registry_scheduler.get_job(job_id) is None:
            client_config = {}
            if 'host' in config:
                client_config['host'] = config['host']
            if 'port' in config:
                client_config['port'] = config['port']
            consul = ConsulClient(**client_config)
            self._do_consul_register(consul, app_settings)
            trigger = IntervalTrigger(minutes=1)
            self._registry_scheduler.add_job(self._do_consul_register,
                                             args=(consul, app_settings),
                                             id=job_id,
                                             trigger=trigger)

    def _do_consul_register(self, consul: ConsulClient, app_settings: Settings):
        local_ip = get_local_ip_address()
        port = app_settings['port']
        service_id = '{}-{}-{}'.format(self.service_name, local_ip, port)
        heath_url = 'http://{}:{}/health'.format(local_ip, port)
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
