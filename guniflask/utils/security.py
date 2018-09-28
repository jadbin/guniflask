# coding=utf-8

import os
import datetime as dt

from flask import _request_ctx_stack
import jwt


def generate_jwt_secret():
    return os.urandom(20).hex()


def load_user(user_loader):
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'user'):
            user = user_loader()
            ctx.user = user
        return ctx.user


def get_payload_from_jwt(token, key, algorithm, **kwargs):
    return jwt.decode(token, key=key, algorithms=[algorithm], **kwargs)


def create_jwt(payload, key, algorithm, expires_in=None, **kwargs):
    if expires_in is not None:
        exp = int(dt.datetime.utcnow().timestamp()) + expires_in
        payload['exp'] = exp
    return jwt.encode(payload, key, algorithm=algorithm, **kwargs)
