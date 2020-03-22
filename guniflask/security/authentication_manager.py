# coding=utf-8

from flask import _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.security.authentication import Authentication

__all__ = ['current_auth', 'AuthenticationManager']


def _load_authentication():
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'authentication'):
            return None
        return ctx.authentication


current_auth = LocalProxy(_load_authentication)


class AuthenticationManager:
    def authenticate(self, authentication: Authentication) -> Authentication:
        raise NotImplemented
