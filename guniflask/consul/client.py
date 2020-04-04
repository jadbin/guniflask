# coding=utf-8

from typing import List

import requests

from guniflask.consul.errors import ConsulClientError

__all__ = ['Consul']


class Consul:
    api_version = 'v1'

    def __init__(self, host: str = '127.0.0.1', port: int = 8500, scheme: str = 'http'):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.session = requests.Session()
        self.base_url = '{}://{}:{}/{}'.format(scheme, host, port, self.api_version)

    def register_service(self, name: str = None,
                         service_id=None,
                         tags: List[str] = None,
                         address: str = None,
                         port: int = None,
                         check_http: str = None,
                         check_interval: int = 10):
        api_path = '/agent/service/register?replace-existing-checks=true'
        data = {
            'Name': name,
            'ID': service_id,
            'Tags': tags,
            'Address': address,
            'Port': port,
            'Check': {
                'Name': name,
                'Interval': '{}s'.format(check_interval),
                'HTTP': check_http
            }
        }
        url = '{}{}'.format(self.base_url, api_path)
        resp = self.session.put(url, json=data)
        if not resp.ok:
            raise ConsulClientError(resp.text)

    def deregister_service(self, service_id: str):
        api_path = '/agent/service/deregister/{}'.format(service_id)
        url = '{}{}'.format(self.base_url, api_path)
        resp = self.session.put(url)
        if not resp.ok:
            raise ConsulClientError(resp.text)
