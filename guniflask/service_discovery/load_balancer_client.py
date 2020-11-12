from abc import ABCMeta, abstractmethod
from urllib.parse import urlsplit

from requests import Session, Request

from guniflask.service_discovery.service_instance import ServiceInstance


class LoadBalancerClient(metaclass=ABCMeta):

    @abstractmethod
    def choose(self, service_name: str) -> ServiceInstance:
        pass  # pragma: no cover

    @abstractmethod
    def reconstruct_url(self, service_instance: ServiceInstance, original_url: str) -> str:
        pass  # pragma: no cover


class RestClient(Session):

    def __init__(self, load_balancer_client: LoadBalancerClient):
        assert load_balancer_client is not None, 'LoadBalancerClient is required'
        self.load_balancer_client = load_balancer_client
        super().__init__()

    def prepare_request(self, request: Request):
        result = urlsplit(request.url)
        if '.' not in result.netloc:
            service_name = result.netloc
            service_instance = self.load_balancer_client.choose(service_name)
            if service_instance is not None:
                request.url = self.load_balancer_client.reconstruct_url(service_instance, request.url)
        return super().prepare_request(request)
