# coding=utf-8

import os
import datetime as dt
import base64
import uuid

import jwt

from flask import _request_ctx_stack


def load_user(user_loader):
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, 'user'):
            user = user_loader()
            ctx.user = user
        return ctx.user


def generate_jwt_secret(n=32):
    return base64.b64encode(os.urandom(n), altchars=b'-_').decode().replace('=', '')


def decode_jwt(token, key, algorithm, **kwargs):
    return jwt.decode(token, key=key, algorithms=[algorithm], **kwargs)


def encode_jwt(payload, key, algorithm, expires_in=None, **kwargs):
    token_data = {
        'jti': str(uuid.uuid4())
    }
    if expires_in is not None:
        if isinstance(expires_in, (int, float)):
            expires_in = dt.timedelta(seconds=expires_in)
        exp = dt.datetime.utcnow().timestamp() + expires_in
        token_data['exp'] = exp
    token_data.update(payload)
    return jwt.encode(token_data, key, algorithm=algorithm, **kwargs)
