# coding=utf-8


from functools import wraps

from flask import current_app, _request_ctx_stack
from werkzeug.local import LocalProxy
from werkzeug.exceptions import Unauthorized

from guniflask.security.authentication import current_auth, OAuth2Authentication, UserAuthentication

__all__ = ['current_user', 'User']


def _load_user():
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'user'):
            user = None
            auth = current_auth._get_current_object()
            if auth is not None:
                if isinstance(auth, OAuth2Authentication):
                    auth = auth.user_authentication
                if isinstance(auth, UserAuthentication):
                    user = User(username=auth.principal, authorities=auth.authorities,
                                details=auth.details)
            ctx.user = user
        return ctx.user


current_user = LocalProxy(_load_user)


class User:
    user_role_prefix = 'role_'

    def __init__(self, username=None, authorities=None, details=None):
        self._username = username
        self._authorities = set()
        if authorities:
            self._authorities.update(authorities)
        self.details = details

    @property
    def username(self):
        return self._username

    @property
    def authorities(self):
        return self._authorities

    def has_authority(self, authority):
        return self.has_any_authority(authority)

    def has_any_authority(self, *authorities):
        return self._has_any_authority_name(None, *authorities)

    def has_role(self, role):
        return self.has_any_role(role)

    def has_any_role(self, *roles):
        prefix = current_app.config.get('USER_ROLE_PREFIX', self.user_role_prefix)
        return self._has_any_authority_name(prefix, *roles)

    def _has_any_authority_name(self, prefix, *roles):
        for role in roles:
            r = self._role_with_prefix(prefix, role)
            if r in self.authorities:
                return True
        return False

    @staticmethod
    def _role_with_prefix(prefix, role):
        if role is None or prefix is None:
            return role
        if role.startswith(prefix):
            return role
        return prefix + role


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user is None:
            raise Unauthorized
        return func(*args, **kwargs)

    return wrapper


def roles_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user is None or not current_user.has_any_role(*roles):
                raise Unauthorized
            return func(*args, **kwargs)

        return wrapper

    return decorator


def authorities_required(*authorities):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user is None or not current_user.has_any_authority(*authorities):
                raise Unauthorized
            return func(*args, **kwargs)

        return wrapper

    return decorator
