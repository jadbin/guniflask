# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.service_discovery.service_instance import ServiceInstance

__all__ = ['LoadBalancerClient']


class LoadBalancerClient(metaclass=ABCMeta):

    @abstractmethod
    def choose(self, service_name: str) -> ServiceInstance:
        pass

    @abstractmethod
    def reconstruct_url(self, service_instance: ServiceInstance, original_url: str) -> str:
        pass
