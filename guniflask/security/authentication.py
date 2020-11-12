from abc import ABCMeta, abstractmethod


class Authentication(metaclass=ABCMeta):
    def __init__(self, authorities=None):
        self._authorities = set()
        if authorities is not None:
            self._authorities.update(authorities)
        self._authenticated = False
        self.details = None

    @property
    @abstractmethod
    def name(self):
        pass  # pragma: no cover

    @property
    @abstractmethod
    def principal(self):
        pass  # pragma: no cover

    @property
    @abstractmethod
    def credentials(self):
        pass  # pragma: no cover

    def authenticate(self, value):
        self._authenticated = value

    @property
    def is_authenticated(self):
        return self._authenticated

    @property
    def authorities(self):
        return self._authorities
