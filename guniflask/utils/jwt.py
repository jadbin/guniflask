# coding=utf-8

import os
import base64

import jwt


def generate_jwt_secret(n=32):
    return base64.b64encode(os.urandom(n), altchars=b'-_').decode().replace('=', '')


def decode_jwt(token, key, algorithm, **kwargs):
    return jwt.decode(token, key=key, algorithms=[algorithm], **kwargs)


def encode_jwt(payload, key, algorithm, **kwargs):
    token = jwt.encode(payload, key, algorithm=algorithm, **kwargs)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token
