from typing import List, Union
from urllib.parse import urlencode, urlsplit, urlunsplit

import dns.message
import dns.query
import dns.rdatatype
import requests

from guniflask.service_discovery.discovery_client import DiscoveryClient
from guniflask.service_discovery.errors import ServiceDiscoveryError
from guniflask.service_discovery.load_balancer_client import LoadBalancerClient
from guniflask.service_discovery.service_instance import ServiceInstance


class ConsulClientError(ServiceDiscoveryError):
    pass


class ConsulClient(DiscoveryClient, LoadBalancerClient):
    api_version = 'v1'

    def __init__(self, host: str = '127.0.0.1', port: int = 8500, dns_port: int = 8600, scheme: str = 'http'):
        self.host = host
        self.port = port
        self.dns_port = dns_port
        self.scheme = scheme
        self.session = requests.Session()
        self.base_url = f'{scheme}://{host}:{port}/{self.api_version}'

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
    def http_check(name: str, url: str, check_id: str = None, interval: str = None, deregister_after: str = None):
        return {'Name': name,
                'CheckID': check_id,
                'HTTP': url,
                'Interval': interval,
                'DeregisterCriticalServiceAfter': deregister_after}

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
