# coding=utf-8

from typing import Union

from flask import _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.context import SecurityContext
from guniflask.oauth2.authentication import OAuth2Authentication
from guniflask.security.user import User

__all__ = ['current_user']


def _load_user() -> Union[User, None]:
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
