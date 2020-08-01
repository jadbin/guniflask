# coding=utf-8

from typing import List
from urllib.parse import urlencode

import requests

from guniflask.service_discovery.errors import ServiceDiscoveryError

__all__ = ['ConsulClient', 'ConsulClientError']


class ConsulClientError(ServiceDiscoveryError):
    pass


class ConsulClient:
    api_version = 'v1'

    def __init__(self, host: str = '127.0.0.1', port: int = 8500, scheme: str = 'http'):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.session = requests.Session()
        self.base_url = '{}://{}:{}/{}'.format(scheme, host, port, self.api_version)

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
            api_path = '{}?{}'.format(api_path, urlencode(args))

        data = {
            'Name': name,
            'ID': service_id,
            'Tags': tags,
            'Address': address,
            'Port': port,
            'Check': check
        }
        url = '{}{}'.format(self.base_url, api_path)
        try:
            resp = self.session.put(url, json=data)
        except Exception as e:
            raise ConsulClientError(e)
        if not resp.ok:
            raise ConsulClientError(resp.text)

    def deregister_service(self, service_id: str):
        api_path = '/agent/service/deregister/{}'.format(service_id)
        url = '{}{}'.format(self.base_url, api_path)
        try:
            resp = self.session.put(url)
        except Exception as e:
            raise ConsulClientError(e)
        if not resp.ok:
            raise ConsulClientError(resp.text)

    def get_service_by_id(self, service_id: str):
        api_path = '/agent/service/{}'.format(service_id)
        url = '{}{}'.format(self.base_url, api_path)
        try:
            resp = self.session.get(url)
        except Exception as e:
            raise ConsulClientError(e)
        if resp.status_code == 200:
            return resp.json()

    @staticmethod
    def http_check(name: str, url: str, check_id: str = None, interval: str = None, deregister_after: str = None):
        return {'Name': name,
                'CheckID': check_id,
                'HTTP': url,
                'Interval': interval,
                'DeregisterCriticalServiceAfter': deregister_after}
