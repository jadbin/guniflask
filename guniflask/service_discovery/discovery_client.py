# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.service_discovery.service_instance import ServiceInstance

__all__ = ['DiscoveryClient']


class DiscoveryClient(metaclass=ABCMeta):

    @abstractmethod
    def get_service_instance(self, service_name: str) -> ServiceInstance:
        pass
