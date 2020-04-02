# coding=utf-8

import os
import base64

import jwt
from json import JSONEncoder as _JSONEncoder

__all__ = ['JwtHelper']


class JsonEncoder(_JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        return super().default(o)


class JwtHelper:
    @staticmethod
    def generate_jwt_secret(n=32):
        return base64.b64encode(os.urandom(n), altchars=b'-_').decode().replace('=', '')

    @staticmethod
    def decode_jwt(token, key, algorithm, **kwargs):
        return jwt.decode(token, key=key, algorithms=[algorithm], **kwargs)

    @staticmethod
    def encode_jwt(payload, key, algorithm, **kwargs):
        token = jwt.encode(payload, key, algorithm=algorithm, json_encoder=JsonEncoder, **kwargs)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return token
