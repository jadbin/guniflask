from abc import ABCMeta, abstractmethod


class UserDetails(metaclass=ABCMeta):

    @property
    @abstractmethod
    def username(self):
        pass  # pragma: no cover

    @property
    @abstractmethod
    def password(self):
        pass  # pragma: no cover

    @property
    @abstractmethod
    def authorities(self):
        pass  # pragma: no cover
