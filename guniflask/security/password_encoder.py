from abc import ABCMeta, abstractmethod


class PasswordEncoder(metaclass=ABCMeta):
    @abstractmethod
    def encode(self, raw_password: bytes) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def matches(self, raw_password: bytes, encoded_password: str) -> bool:
        pass  # pragma: no cover


class PlainPasswordEncoder(PasswordEncoder):
    def encode(self, raw_password: bytes) -> str:
        if not raw_password:
            return ''
        return raw_password.decode('utf-8')

    def matches(self, raw_password: bytes, encoded_password: str) -> bool:
        if raw_password is None:
            raw_password = b''
        if encoded_password is None:
            encoded_password = ''
        return raw_password.decode('utf-8') == encoded_password
