# coding=utf-8

from typing import Optional

from flask import _request_ctx_stack

from guniflask.security.authentication import Authentication

__all__ = ['SecurityContext']


class SecurityContext:
    AUTHENTICATION = '__authentication'

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
