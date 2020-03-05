# coding=utf-8

import os
import base64
import datetime as dt
import uuid

import jwt
from flask import current_app, _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.authentication import UserAuthentication
from guniflask.security.authentication_manager import AuthenticationManager, BearerTokenExtractor
from guniflask.security.token import OAuth2AccessToken
from guniflask.security.errors import InvalidTokenError
from guniflask.security.token_converter import AccessTokenConverter, JwtAccessTokenConverter, \
    UserAuthenticationConverter

__all__ = ['JwtHelper', 'jwt_manager', 'JwtManager']


class JwtHelper:
    @staticmethod
    def generate_jwt_secret(n=32):
        return base64.b64encode(os.urandom(n), altchars=b'-_').decode().replace('=', '')

    @staticmethod
    def decode_jwt(token, key, algorithm, **kwargs):
        return jwt.decode(token, key=key, algorithms=[algorithm], **kwargs)

    @staticmethod
    def encode_jwt(payload, key, algorithm, **kwargs):
        token = jwt.encode(payload, key, algorithm=algorithm, **kwargs)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return token


jwt_manager = LocalProxy(lambda: current_app.extensions['jwt_manager'])


class JwtManager(AuthenticationManager):
    EXP = AccessTokenConverter.EXP
    JTI = AccessTokenConverter.JTI
    AUTHORITIES = AccessTokenConverter.AUTHORITIES
    USERNAME = UserAuthenticationConverter.USERNAME
    USER_DETAILS = 'user_details'

    def __init__(self):
        self.token_extractor = BearerTokenExtractor()
        self.token_converter = JwtAccessTokenConverter()

    def init_app(self, app):
        self._set_default_app_config(app)
        app.extensions['jwt_manager'] = self

    def _set_default_app_config(self, app):
        app.config.setdefault('JWT_ALGORITHM', 'HS256')
        app.config.setdefault('JWT_SECRET', None)
        app.config.setdefault('JWT_PRIVATE_KEY', None)
        app.config.setdefault('JWT_PUBLIC_KEY', None)
        app.config.setdefault('ACCESS_TOKEN_EXPIRES_IN', dt.timedelta(days=1))
        app.config.setdefault('REFRESH_TOKEN_EXPIRES_IN', dt.timedelta(days=365))

    def create_access_token(self, authorities=None, username=None, user_details=None) -> str:
        app_config = current_app.config

        expires_in = app_config['ACCESS_TOKEN_EXPIRES_IN']
        payload = {
            self.JTI: str(uuid.uuid4())
        }
        exp = dt.datetime.utcnow() + expires_in
        payload[self.EXP] = exp

        payload[self.AUTHORITIES] = authorities
        payload[self.USERNAME] = username
        payload[self.USER_DETAILS] = user_details

        return JwtHelper.encode_jwt(payload, app_config['JWT_SECRET'] or app_config['JWT_PRIVATE_KEY'],
                                    app_config['JWT_ALGORITHM'])

    def read_access_token(self, access_token_value: str) -> OAuth2AccessToken:
        payload = self._decode(access_token_value)
        return self.token_converter.extract_access_token(access_token_value, payload)

    def authenticate(self, authentication):
        access_token_value = authentication.principal
        payload = self._decode(access_token_value)
        authorities = payload[self.AUTHORITIES]
        username = payload[self.USERNAME]
        user_details = payload[self.USER_DETAILS]
        user_auth = UserAuthentication(username, authorities=authorities)
        user_auth.details = user_details
        user_auth.authenticate(True)
        return user_auth

    def _decode(self, access_token_value):
        app_config = current_app.config
        try:
            payload = JwtHelper.decode_jwt(access_token_value, app_config['JWT_SECRET'] or app_config['JWT_PUBLIC_KEY'],
                                           app_config['JWT_ALGORITHM'])
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
