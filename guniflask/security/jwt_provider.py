# coding=utf-8

import datetime as dt
import uuid

from flask import current_app
from werkzeug.local import LocalProxy

from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.oauth2.errors import InvalidTokenError
from guniflask.oauth2.token import OAuth2AccessToken
from guniflask.oauth2.token_converter import AccessTokenConverter, JwtAccessTokenConverter, \
    UserAuthenticationConverter
from guniflask.security.user import User
from guniflask.security.jwt import JwtHelper

__all__ = ['jwt_manager', 'JwtManager']

jwt_manager = LocalProxy(lambda: current_app.extensions['jwt_manager'])


class JwtManager(AuthenticationManager):
    EXP = AccessTokenConverter.EXP
    JTI = AccessTokenConverter.JTI
    AUTHORITIES = AccessTokenConverter.AUTHORITIES
    USERNAME = UserAuthenticationConverter.USERNAME
    USER_DETAILS = 'user_details'

    def __init__(self, secret='', public_key=None, private_key=None, algorithm='HS256',
                 access_token_expires_in=24 * 60 * 60, refresh_token_expires_in=365 * 24 * 60 * 60):
        self.secret = secret
        self.public_key = public_key
        self.private_key = private_key
        self.algorithm = algorithm
        self.access_token_expires_in = access_token_expires_in
        self.refresh_token_expires_in = refresh_token_expires_in

        self.token_converter = JwtAccessTokenConverter()

        app = current_app._get_current_object()
        app.extensions['jwt_manager'] = self

    def create_access_token(self, authorities=None, username=None, **user_details) -> str:
        expires_in = self.access_token_expires_in
        payload = {
            self.JTI: uuid.uuid4().hex
        }
        exp = dt.datetime.now() + dt.timedelta(seconds=expires_in)
        payload[self.EXP] = exp

        payload[self.AUTHORITIES] = authorities
        payload[self.USERNAME] = username
        payload[self.USER_DETAILS] = user_details

        return JwtHelper.encode_jwt(payload, self.secret or self.private_key,
                                    self.algorithm)

    def read_access_token(self, access_token_value: str) -> OAuth2AccessToken:
        payload = self._decode(access_token_value)
        return self.token_converter.extract_access_token(access_token_value, payload)

    def authenticate(self, authentication):
        access_token_value = authentication.principal
        payload = self._decode(access_token_value)
        authorities = payload[self.AUTHORITIES]
        username = payload[self.USERNAME]
        user_details = payload[self.USER_DETAILS]
        user = User(username=username, authorities=authorities)
        for k, v in user_details.items():
            setattr(user, k, v)
        user_auth = UserAuthentication(user, authorities=authorities)
        user_auth.authenticate(True)
        return user_auth

    def _decode(self, access_token_value):
        try:
            payload = JwtHelper.decode_jwt(access_token_value, self.secret or self.public_key,
                                           self.algorithm)
        except Exception as e:
            raise InvalidTokenError(e)
        return payload
