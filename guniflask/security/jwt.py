# coding=utf-8

import datetime as dt

from flask import current_app, request
from jwt import InvalidTokenError

from guniflask.utils.security import encode_jwt, decode_jwt
from guniflask.security.user import AnonymousUser, User
from guniflask.security.auth import AuthManager

__all__ = ['JwtManager']


class JwtManager(AuthManager):
    def __init__(self, app=None):
        super().__init__(app=app)
        self._user_loader = self._load_user_from_header

    def init_app(self, app):
        self._set_default_app_config(app)
        app.extensions['jwt_manager'] = self
        super().init_app(app)

    def _set_default_app_config(self, app):
        app.config.setdefault('JWT_ALGORITHM', 'HS256')
        app.config.setdefault('JWT_SECRET', None)
        app.config.setdefault('JWT_PRIVATE_KEY', None)
        app.config.setdefault('JWT_PUBLIC_KEY', None)
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES_IN', dt.timedelta(days=1))

    def create_access_token(self, authorities=None, expires_in=None, **kwargs):
        config = current_app.config
        user_claims = dict(kwargs)
        user_claims['authorities'] = authorities
        payload = {'user_claims': user_claims}
        if expires_in is None:
            expires_in = config['JWT_ACCESS_TOKEN_EXPIRES_IN']
        return encode_jwt(payload, config['JWT_SECRET'] or config['JWT_PRIVATE_KEY'],
                          config['JWT_ALGORITHM'], expires_in=expires_in)

    def _load_user_from_header(self):
        config = current_app.config
        user = AnonymousUser()
        token = self.current_token
        if token:
            try:
                payload = decode_jwt(token, config['JWT_SECRET'] or config['JWT_PUBLIC_KEY'],
                                     config['JWT_ALGORITHM'])
            except InvalidTokenError:
                pass
            else:
                user_claims = payload['user_claims']
                user = User(**user_claims)
        return user

    @property
    def current_token(self):
        token = self._get_token_from_header()
        if token is None:
            token = self._get_token_from_query()
        return token

    @staticmethod
    def _get_token_from_header():
        auth = request.headers.get('Authorization')
        if auth is not None and auth.startswith('Bearer'):
            return auth.split(' ', 1)[1]

    @staticmethod
    def _get_token_from_query():
        return request.args.get('access_token')
