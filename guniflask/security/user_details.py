# coding=utf-8

from abc import ABCMeta, abstractmethod


class UserDetails(metaclass=ABCMeta):

    @property
    @abstractmethod
    def username(self):
        pass

    @property
    @abstractmethod
    def password(self):
        pass

    @property
    @abstractmethod
    def authorities(self):
        pass
