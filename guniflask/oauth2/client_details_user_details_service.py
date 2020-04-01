# coding=utf-8

from guniflask.security.user_details import UserDetails
from guniflask.security.user_details_service import UserDetailsService
from guniflask.oauth2.client_details_service import ClientDetailsService
from guniflask.security.password_encoder import PasswordEncoder
from guniflask.oauth2.errors import NoSuchClientError
from guniflask.security.errors import UsernameNotFoundError
from guniflask.security.user import User

__all__ = ['ClientDetailsUserDetailsService']


class ClientDetailsUserDetailsService(UserDetailsService):

    def __init__(self, client_details_service: ClientDetailsService):
        self.client_details_service = client_details_service
        self.empty_password = ""

    def set_password_encoder(self, password_encoder: PasswordEncoder):
        self.empty_password = password_encoder.encode(b'')

    def load_user_by_username(self, username: str) -> UserDetails:
        try:
            client_details = self.client_details_service.load_client_details_by_client_id(username)
        except NoSuchClientError as e:
            raise UsernameNotFoundError(e)
        client_secret = client_details.client_secret
        if not client_secret:
            client_secret = self.empty_password
        return User(username=username, password=client_secret, authorities=client_details.authorities)
