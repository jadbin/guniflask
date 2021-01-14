from typing import Optional

from flask import _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.authentication import Authentication
from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.user import User
from guniflask.security.user_details import UserDetails


class SecurityContext:
    AUTHENTICATION = '__authentication'
    USER = '__user'

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


current_user = LocalProxy(SecurityContext.get_user)
