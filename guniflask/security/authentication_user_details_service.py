from abc import ABCMeta, abstractmethod

from guniflask.security.authentication import Authentication
from guniflask.security.user_details import UserDetails


class AuthenticationUserDetailsService(metaclass=ABCMeta):
    @abstractmethod
    def load_user_details(self, token: Authentication) -> UserDetails:
        pass  # pragma: no cover
