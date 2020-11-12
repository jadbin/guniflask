from abc import ABCMeta, abstractmethod

from guniflask.security.authentication import Authentication


class AuthenticationManager(metaclass=ABCMeta):
    @abstractmethod
    def authenticate(self, authentication: Authentication) -> Authentication:
        pass  # pragma: no cover
