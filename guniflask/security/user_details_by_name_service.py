# coding=utf-8

from guniflask.security.authentication import Authentication
from guniflask.security.user_details import UserDetails
from guniflask.security.authentication_user_details_service import AuthenticationUserDetailsService
from guniflask.security.user_details_service import UserDetailsService

__all__ = ['UserDetailsByNameService']


class UserDetailsByNameService(AuthenticationUserDetailsService):
    def __init__(self, user_details_service: UserDetailsService):
        self._user_details_service = user_details_service

    def load_user_details(self, token: Authentication) -> UserDetails:
        return self._user_details_service.load_user_by_username(token.name)
