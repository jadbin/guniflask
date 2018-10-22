# coding=utf-8

import datetime as dt

from flask import current_app, _request_ctx_stack, request
from jwt import InvalidTokenError
from werkzeug.local import LocalProxy

from guniflask.utils.security import encode_jwt, decode_jwt


def _load_user():
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'user'):
            user = current_app.extensions['auth_manager'].load_user()
            ctx.user = user
        return ctx.user


current_user = LocalProxy(_load_user)
auth_manager = LocalProxy(current_app.extensions['auth_manager'])


class AuthManager:
    def __init__(self, app=None):
        self._user_loader = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['auth_manager'] = self

    def user_loader(self, func):
        self._user_loader = func
        return func

    def load_user(self):
        if self._user_loader is None:
            raise RuntimeError('Missing user loader')
        return self._user_loader()


class User:
    ROLE_PREFIX = 'role_'

    def __init__(self, authorities=None, **kwargs):
        self.authorities = set()
        for a in authorities:
            self.authorities.add(a.lower())
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def is_authenticated(self):
        return True

    def has_authority(self, authority):
        authority = authority.lower()
        return authority in self.authorities

    def has_any_authority(self, *authorities):
        for a in authorities:
            if self.has_authority(a):
                return True
        return False

    def has_role(self, role):
        role = role.lower()
        if not role.startswith(self.ROLE_PREFIX):
            role = self.ROLE_PREFIX + role
        return role in self.authorities

    def has_any_role(self, *roles):
        for r in roles:
            if self.has_role(r):
                return True
        return False


class AnonymousUser(User):
    @property
    def is_authenticated(self):
        return False

    def has_authority(self, authority):
        return False

    def has_any_authority(self, *authorities):
        return False

    def has_role(self, role):
        return False

    def has_any_role(self, *roles):
        return False


class JwtAuthManager(AuthManager):
    def __init__(self, app=None):
        self._user_loader = self.load_user_from_header
        super().__init__(app=app)

    def init_app(self, app):
        self._set_default_app_config(app)
        super().init_app(app)

    @staticmethod
    def _set_default_app_config(app):
        app.config.setdefault('JWT_ALGORITHM', 'HS256')
        app.config.setdefault('JWT_SECRET', None)
        app.config.setdefault('JWT_PRIVATE_KEY', None)
        app.config.setdefault('JWT_PUBLIC_KEY', None)
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES_IN', dt.timedelta(days=1))

    @staticmethod
    def create_access_token(authorities=None, expires_in=None, **kwargs):
        config = current_app.config
        user_claims = dict(kwargs)
        user_claims['authorities'] = authorities
        payload = {'user_claims': user_claims}
        if expires_in is None:
            expires_in = config['JWT_ACCESS_TOKEN_EXPIRES_IN']
        return encode_jwt(payload, config['JWT_SECRET'] or config['JWT_PRIVATE_KEY'],
                          config['JWT_ALGORITHM'], expires_in=expires_in)

    @staticmethod
    def load_user_from_header():
        config = current_app.config
        auth = request.headers.get('Authorization')
        user = AnonymousUser()
        if auth is not None and auth.starts_with('Bearer'):
            try:
                payload = decode_jwt(auth.split(' ', 1)[1], config['JWT_SECRET'] or config['JWT_PUBLIC_KEY'],
                                     config['JWT_ALGORITHM'])
            except InvalidTokenError:
                pass
            else:
                user_claims = payload['user_claims']
                user = User(**user_claims)
        return user
