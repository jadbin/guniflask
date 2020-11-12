from abc import ABCMeta, abstractmethod

from guniflask.security.user_details_service import UserDetailsService
from guniflask.security_config.security_configurer import SecurityConfigurer


class UserDetailsAwareConfigurer(SecurityConfigurer, metaclass=ABCMeta):
    @property
    @abstractmethod
    def user_details_service(self) -> UserDetailsService:
        pass  # pragma: no cover
