from abc import ABCMeta, abstractmethod
from typing import List

from guniflask.service_discovery.service_instance import ServiceInstance


class DiscoveryClient(metaclass=ABCMeta):

    @abstractmethod
    def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        pass  # pragma: no cover
