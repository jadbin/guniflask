import base64
import io
import json
import logging
from typing import List, Union, Optional
from urllib.parse import urlencode, urlsplit, urlunsplit

import dns.message
import dns.query
import dns.rdatatype
import requests
import yaml

from guniflask.config.app_settings import settings
from guniflask.context.annotation import condition_on_setting, configuration
from guniflask.service_discovery.config import ServiceDiscoveryConfigurer
from guniflask.service_discovery.discovery_client import DiscoveryClient
from guniflask.service_discovery.errors import ServiceDiscoveryError
from guniflask.service_discovery.load_balancer_client import LoadBalancerClient
from guniflask.service_discovery.service_instance import ServiceInstance

log = logging.getLogger(__name__)


class ConsulClientError(ServiceDiscoveryError):
    pass


class ConsulClient(DiscoveryClient, LoadBalancerClient):
    api_version = 'v1'

    def __init__(
            self,
            host: str = '127.0.0.1',
            port: int = 8500,
            dns_port: int = 8600,
            scheme: str = 'http',
            config_key: str = None,
            config_format: str = 'yaml',
    ):
        self.host = host
        self.port = port
        self.dns_port = dns_port
        self.scheme = scheme
        self.session = requests.Session()
        self.base_url = f'{scheme}://{host}:{port}/{self.api_version}'

        config_format = config_format.lower()
        assert config_format in {'yaml', 'json'}, \
            f'unsupported Consul configuration format: {config_format}'
        self.config_format = config_format
        if config_key:
            remote_settings = self.get_configuration(config_key)
            if remote_settings:
                settings.merge(remote_settings)

    def register_service(self, name: str,
                         service_id: str = None,
                         tags: List[str] = None,
                         address: str = None,
                         port: int = None,
                         check: dict = None):
        api_path = '/agent/service/register'
        args = {}
        if check is not None:
            args['replace-existing-checks'] = 'true'
        if len(args) > 0:
            api_path = f'{api_path}?{urlencode(args)}'

        data = {
            'Name': name,
            'ID': service_id,
            'Tags': tags,
            'Address': address,
            'Port': port,
            'Check': check
        }
        url = f'{self.base_url}{api_path}'
        try:
            resp = self.session.put(url, json=data)
            resp.raise_for_status()
        except Exception as e:
            raise ConsulClientError(e)

    def deregister_service(self, service_id: str):
        api_path = f'/agent/service/deregister/{service_id}'
        url = f'{self.base_url}{api_path}'
        try:
            resp = self.session.put(url)
            resp.raise_for_status()
        except Exception as e:
            raise ConsulClientError(e)

    def get_service_by_id(self, service_id: str):
        api_path = f'/agent/service/{service_id}'
        url = f'{self.base_url}{api_path}'
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
        except Exception as e:
            raise ConsulClientError(e)
        return resp.json()

    @staticmethod
    def http_check(
            name: str,
            url: str,
            check_id: str = None,
            interval: str = None,
            deregister_after: str = None):
        return {
            'Name': name,
            'CheckID': check_id,
            'HTTP': url,
            'Interval': interval,
            'DeregisterCriticalServiceAfter': deregister_after,
        }

    def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        api_path = f'/agent/health/service/name/{service_name}'
        url = f'{self.base_url}{api_path}'
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
        except Exception as e:
            raise ConsulClientError(e)
        data = resp.json()
        services = []
        for d in data:
            if d['AggregatedStatus'] == 'passing':
                s = d['Service']
                services.append(ServiceInstance(service_id=s['ID'],
                                                host=s['Address'],
                                                port=s['Port']))
        return services

    def choose(self, service_name: str) -> Union[ServiceInstance, None]:
        request = dns.message.make_query(f'{service_name}.service.consul', dns.rdatatype.SRV)
        response = dns.query.udp(request, self.host, port=self.dns_port)
        if len(response.answer) > 0:
            answer = response.answer[0]
            port = None
            target = None
            for k in answer:
                port = k.port
                target = k.target
                break
            if target is not None:
                for additional in response.additional:
                    if additional.name == target:
                        for k in additional:
                            return ServiceInstance(host=k.address, port=port)

    def reconstruct_url(self, service_instance: ServiceInstance, original_url: str) -> str:
        result = urlsplit(original_url)
        result = result._replace(netloc=f'{service_instance.host}:{service_instance.port}')
        return urlunsplit(result)

    def get_configuration(self, key: str, config_format: str = None) -> Optional[dict]:
        if not key:
            return
        if config_format is None:
            config_format = self.config_format

        api_path = f'/kv/{key}'
        url = f'{self.base_url}{api_path}'
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
        except Exception as e:
            raise ConsulClientError(e)
        data = resp.json()[0]['Value']
        s = base64.b64decode(data)
        if config_format == 'yaml':
            return yaml.safe_load(io.BytesIO(s))
        if config_format == 'json':
            return json.load(io.BytesIO(s))


@condition_on_setting('guniflask.consul')
@configuration
class ConsulConfigurer(ServiceDiscoveryConfigurer):

    def __init__(self):
        self._discovery_client: Optional[DiscoveryClient] = None
        self._load_balancer_client: Optional[LoadBalancerClient] = None
        self._service_name: Optional[str] = None
        self._consul_client: Optional[ConsulClient] = None

    @property
    def discovery_client(self) -> DiscoveryClient:
        return self._discovery_client

    @property
    def load_balancer_client(self) -> LoadBalancerClient:
        return self._load_balancer_client

    def configure(self, service_name: str):
        config = settings.get_by_prefix('guniflask.consul')
        self._service_name = service_name
        self._register(config)

    def _register(self, config: dict):
        self._consul_client = ConsulClient(**config)
        self._discovery_client = self._consul_client
        self._load_balancer_client = self._consul_client
        self._do_register(self._consul_client)

    def _do_register(self, consul: ConsulClient):
        local_ip = settings['ip_address']
        port = settings['port']
        service_id = f'{settings["app_name"]}-{local_ip}-{port}'
        heath_url = f'http://{local_ip}:{port}/health?' \
                    f'app_name={settings["app_name"]}'
        try:
            consul.register_service(
                settings['app_name'],
                service_id=service_id,
                address=local_ip,
                port=port,
                check=consul.http_check(
                    service_id,
                    heath_url,
                    check_id=service_id,
                    interval='10s',
                    deregister_after='10m',
                )
            )
        except ConsulClientError as e:
            log.error('Failed to register service to Consul at %s:%s: %s', consul.host, consul.port, e)
