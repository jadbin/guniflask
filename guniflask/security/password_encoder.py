# coding=utf-8

from abc import ABCMeta, abstractmethod

__all__ = ['PasswordEncoder']


class PasswordEncoder(metaclass=ABCMeta):
    @abstractmethod
    def encode(self, raw_password: bytes) -> str:
        pass

    @abstractmethod
    def matches(self, raw_password: bytes, encoded_password: str) -> bool:
        pass
