# coding=utf-8

import datetime as dt
import uuid

from flask import current_app, _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.oauth2.errors import InvalidTokenError
from guniflask.config.utils import map_dict_config
from guniflask.oauth2.authentication_manager import BearerTokenExtractor
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

    class JwtManagerConfig:
        secret = ''
        public_key = None
        private_key = None
        algorithm = 'HS256'
        access_token_expires_in = dt.timedelta(days=1)
        refresh_token_expires_in = dt.timedelta(days=365)

    def __init__(self):
        self.token_extractor = BearerTokenExtractor()
        self.token_converter = JwtAccessTokenConverter()
        self.config = self.JwtManagerConfig()

    @classmethod
    def from_config(cls, config: dict):
        obj = cls()
        map_dict_config(config, obj.config)
        return obj

    def init_app(self, app):
        app.before_request(self.do_authentication_filter)
        app.extensions['jwt_manager'] = self

    def create_access_token(self, authorities=None, username=None, user_details=None) -> str:
        expires_in = self.config.access_token_expires_in
        payload = {
            self.JTI: str(uuid.uuid4())
        }
        exp = dt.datetime.utcnow() + expires_in
        payload[self.EXP] = exp

        payload[self.AUTHORITIES] = authorities
        payload[self.USERNAME] = username
        payload[self.USER_DETAILS] = user_details

        return JwtHelper.encode_jwt(payload, self.config.secret or self.config.private_key,
                                    self.config.algorithm)

    def read_access_token(self, access_token_value: str) -> OAuth2AccessToken:
        payload = self._decode(access_token_value)
        return self.token_converter.extract_access_token(access_token_value, payload)

    def authenticate(self, authentication):
        access_token_value = authentication.principal
        payload = self._decode(access_token_value)
        authorities = payload[self.AUTHORITIES]
        username = payload[self.USERNAME]
        user_details = payload[self.USER_DETAILS]
        user = User(username=username, authorities=authorities, details=user_details)
        user_auth = UserAuthentication(user, authorities=authorities)
        user_auth.authenticate(True)
        return user_auth

    def _decode(self, access_token_value):
        try:
            payload = JwtHelper.decode_jwt(access_token_value, self.config.secret or self.config.public_key,
                                           self.config.algorithm)
        except Exception as e:
            raise InvalidTokenError(e)
        return payload

    def do_authentication_filter(self):
        auth = self.token_extractor.extract()
        if auth is not None:
            user_auth = self.authenticate(auth)
            ctx = _request_ctx_stack.top
            if ctx is not None:
                ctx.authentication = user_auth
