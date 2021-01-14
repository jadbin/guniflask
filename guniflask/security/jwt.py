import base64
import os
from json import JSONEncoder as _JSONEncoder

import jwt


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
    def decode_jwt(token, key, algorithms=None, **kwargs):
        if algorithms is None:
            header = jwt.get_unverified_header(token)
            algorithms = [header['alg']]

        return jwt.decode(token, key=key, algorithms=algorithms, **kwargs)

    @staticmethod
    def encode_jwt(payload, key, algorithm=None, **kwargs):
        token = jwt.encode(payload, key, algorithm=algorithm or 'HS256', json_encoder=JsonEncoder, **kwargs)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return token
