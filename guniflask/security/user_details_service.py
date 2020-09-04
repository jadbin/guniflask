# coding=utf-8

from abc import ABCMeta, abstractmethod

from guniflask.security.user_details import UserDetails


class UserDetailsService(metaclass=ABCMeta):

    @abstractmethod
    def load_user_by_username(self, username: str) -> UserDetails:
        pass
