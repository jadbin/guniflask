import datetime as dt
import uuid

from guniflask.security import Authentication
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.errors import InvalidTokenError
from guniflask.security.jwt import JwtHelper
from guniflask.security.user import User


class JwtManager(AuthenticationManager):
    EXP = 'exp'
    JTI = 'jti'
    AUTHORITIES = 'authorities'
    USERNAME = 'username'
    USERINFO = 'userinfo'

    def __init__(self, secret='', public_key=None, private_key=None, algorithm=None,
                 access_token_expires_in=12 * 60 * 60, refresh_token_expires_in=30 * 24 * 60 * 60):
        self.secret = secret
        self.public_key = public_key
        self.private_key = private_key
        self.algorithm = algorithm
        self.access_token_expires_in = access_token_expires_in
        self.refresh_token_expires_in = refresh_token_expires_in

    def create_access_token(self, authorities=None, username=None, **userinfo) -> str:
        expires_in = self.access_token_expires_in
        payload = {
            self.JTI: uuid.uuid4().hex
        }
        exp = dt.datetime.now() + dt.timedelta(seconds=expires_in)
        payload[self.EXP] = exp

        payload[self.AUTHORITIES] = authorities
        payload[self.USERNAME] = username
        payload[self.USERINFO] = userinfo

        return JwtHelper.encode_jwt(
            payload,
            self.secret or self.private_key,
            algorithm=self.algorithm,
        )

    def authenticate(self, authentication: Authentication):
        access_token_value = authentication.principal
        payload = self._decode(access_token_value)
        authorities = payload.get(self.AUTHORITIES)
        username = payload.get(self.USERNAME)
        userinfo = payload.get(self.USERINFO)
        user = User(username=username, authorities=authorities)
        if userinfo and isinstance(userinfo, dict):
            for k, v in userinfo.items():
                setattr(user, k, v)
        user_auth = UserAuthentication(user, authorities=authorities)
        user_auth.authenticate(True)
        return user_auth

    def _decode(self, access_token_value):
        try:
            payload = JwtHelper.decode_jwt(
                access_token_value,
                self.secret or self.public_key,
                algorithms=[self.algorithm] if self.algorithm else None,
            )
        except Exception as e:
            raise InvalidTokenError(e)
        return payload
