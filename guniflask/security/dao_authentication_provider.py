# coding=utf-8

from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.user_details_authentication_provider import UserDetailsAuthenticationProvider
from guniflask.security.user_details_service import UserDetailsService
from guniflask.security.password_encoder import PasswordEncoder, PlainPasswordEncoder
from guniflask.security.user_details import UserDetails
from guniflask.security.errors import BadCredentialsError

__all__ = ['DaoAuthenticationProvider']


class DaoAuthenticationProvider(UserDetailsAuthenticationProvider):
    def __init__(self, user_details_service: UserDetailsService = None, password_encoder: PasswordEncoder = None):
        super().__init__()
        self.user_details_service = user_details_service
        if password_encoder is None:
            self.password_encoder = PlainPasswordEncoder()
        else:
            self.password_encoder = password_encoder

    def retrieve_user(self, username: str, authentication: UserAuthentication) -> UserDetails:
        user = self.user_details_service.load_user_by_username(username)
        return user

    def check_authentication(self, user_details: UserDetails, authentication: UserAuthentication):
        if authentication.credentials is None:
            raise BadCredentialsError('No credentials provided')
        raw_password = str(authentication.credentials).encode('utf-8')
        if not self.password_encoder.matches(raw_password, user_details.password):
            raise BadCredentialsError('Bad credentials')
