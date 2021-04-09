from typing import Optional, Collection, Union

from flask import _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.authentication import Authentication
from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.user import User
from guniflask.security.user_details import UserDetails


class SecurityContext:
    AUTHENTICATION = '__authentication'
    USER = '__user'
    DEFAULT_ROLE_PREFIX = 'role_'

    @classmethod
    def get_authentication(cls) -> Optional[Authentication]:
        ctx = _request_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, cls.AUTHENTICATION):
                return None
            return getattr(ctx, cls.AUTHENTICATION)

    @classmethod
    def set_authentication(cls, authentication: Authentication):
        ctx = _request_ctx_stack.top
        if ctx is not None:
            setattr(ctx, cls.AUTHENTICATION, authentication)

    @classmethod
    def get_user(cls) -> Optional[User]:
        ctx = _request_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, cls.USER):
                user = None
                auth = cls.get_authentication()
                if auth is not None:
                    if isinstance(auth, UserAuthentication):
                        if isinstance(auth.principal, UserDetails):
                            user = auth.principal
                        else:
                            user = User(username=auth.name, authorities=auth.authorities)
                setattr(ctx, cls.USER, user)
            return getattr(ctx, cls.USER)

    @classmethod
    def has_authority(cls, user: User, authority: str):
        return cls.has_any_authority(user, [authority])

    @classmethod
    def has_any_authority(cls, user: User, authorities: Collection[str]):
        return cls._has_any_authority_name(user, None, authorities)

    @classmethod
    def has_role(cls, user: User, role: str):
        return cls.has_any_role(user, role)

    @classmethod
    def has_any_role(cls, user, roles: Collection[str]):
        return cls._has_any_authority_name(user, cls.DEFAULT_ROLE_PREFIX, roles)

    @classmethod
    def _has_any_authority_name(cls, user: User, prefix: Union[None, str], roles: Collection[str]):
        def role_with_prefix():
            if role is None or prefix is None:
                return role
            if role.startswith(prefix):
                return role
            return prefix + role

        for role in roles:
            r = role_with_prefix()
            if r in user.authorities:
                return True
        return False


class CurrentUser:
    def __init__(self):
        self._user = SecurityContext.get_user()

    def __getattribute__(self, name):
        _user = super().__getattribute__('_user')
        if hasattr(_user, name):
            return getattr(_user, name)
        return super().__getattribute__(name)

    def has_authority(self, authority):
        return SecurityContext.has_authority(self._user, authority)

    def has_any_authority(self, *authorities):
        return SecurityContext.has_any_authority(self._user, authorities)

    def has_role(self, role):
        return SecurityContext.has_role(self._user, role)

    def has_any_role(self, *roles):
        return SecurityContext.has_any_role(self._user, roles)


current_user: Union[LocalProxy, CurrentUser, User] = LocalProxy(CurrentUser)
