from typing import Optional

from flask import _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.context import SecurityContext
from guniflask.security.user import User
from guniflask.security.user_details import UserDetails


class UserContext:
    USER = '__user'

    @classmethod
    def get_user(cls) -> Optional[User]:
        ctx = _request_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, cls.USER):
                user = None
                auth = SecurityContext.get_authentication()
                if auth is not None:
                    if isinstance(auth, UserAuthentication):
                        if isinstance(auth.principal, UserDetails):
                            user = auth.principal
                        else:
                            user = User(username=auth.name, authorities=auth.authorities)
                setattr(ctx, cls.USER, user)
            return getattr(ctx, cls.USER)


current_user = LocalProxy(UserContext.get_user)
