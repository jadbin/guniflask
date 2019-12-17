# coding=utf-8

from functools import wraps

from flask import current_app, _request_ctx_stack, abort
from werkzeug.local import LocalProxy

__all__ = ['current_user', 'auth_manager', 'AuthManager',
           'login_required', 'roles_required', 'authorities_required']

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
