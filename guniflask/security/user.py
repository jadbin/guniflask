# coding=utf-8

from flask import current_app, _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.context import SecurityContext
from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.security.user_details import UserDetails

__all__ = ['current_user', 'User']


def _load_user():
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'user'):
            user = None
            auth = SecurityContext.get_authentication()
            if auth is not None:
                if isinstance(auth, OAuth2Authentication):
                    auth = auth.user_authentication
                if isinstance(auth, UserAuthentication):
                    user = auth.principal
            ctx.user = user
        return ctx.user


current_user = LocalProxy(_load_user)


class User(UserDetails):
    user_role_prefix = 'role_'

    def __init__(self, username=None, authorities=None, details=None):
        super().__init__(username=username, authorities=authorities)
        self.details = details

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
