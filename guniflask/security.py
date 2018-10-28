# coding=utf-8

import datetime as dt
from functools import wraps

from flask import current_app, _request_ctx_stack, request, abort
from jwt import InvalidTokenError
from werkzeug.local import LocalProxy

from guniflask.utils.security import encode_jwt, decode_jwt

auth_manager = LocalProxy(lambda: current_app.extensions['auth_manager'])


def _load_user():
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'user'):
            user = auth_manager.load_user()
            ctx.user = user
        return ctx.user


current_user = LocalProxy(_load_user)


class AuthManager:
    def __init__(self, app=None):
        self._user_loader = None
        self._unauthorized_handler = None
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

    @property
    def unauthorized_view(self):
        if self._unauthorized_handler:
            return self._unauthorized_handler()
        return abort(401)

    def unauthorized(self, func):
        self._unauthorized_handler = func
        return func


class User:
    ROLE_PREFIX = 'role_'

    def __init__(self, authorities=None, **kwargs):
        self.authorities = []
        if authorities is not None:
            for a in authorities:
                self.authorities.append(a.lower())
        self._authorities_set = set(self.authorities)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def is_authenticated(self):
        return True

    def has_authority(self, authority):
        authority = authority.lower()
        return authority in self._authorities_set

    def has_any_authority(self, *authorities):
        for a in authorities:
            if self.has_authority(a):
                return True
        return False

    def has_role(self, role):
        return self.has_authority(self._get_role_with_prefix(self.ROLE_PREFIX, role))

    def has_any_role(self, *roles):
        for r in roles:
            if self.has_role(r):
                return True
        return False

    @staticmethod
    def _get_role_with_prefix(prefix, role):
        if role is None or prefix is None:
            return role
        if role.startswith(prefix):
            return role
        return prefix + role


class AnonymousUser(User):
    def __init__(self, authorities=None, **kwargs):
        super().__init__(**kwargs)

    @property
    def is_authenticated(self):
        return False


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return auth_manager.unauthorized_view
        return func(*args, **kwargs)

    return wrapper


def roles_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user is None or not current_user.has_any_role(*roles):
                return auth_manager.unauthorized_view
            return func(*args, **kwargs)

        return wrapper

    return decorator


def authorities_required(*authorities):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user is None or not current_user.has_any_authority(*authorities):
                return auth_manager.unauthorized_view
            return func(*args, **kwargs)

        return wrapper

    return decorator


class JwtAuthManager(AuthManager):
    def __init__(self, app=None):
        super().__init__(app=app)
        self._user_loader = self._load_user_from_header

    def init_app(self, app):
        self._set_default_app_config(app)
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
