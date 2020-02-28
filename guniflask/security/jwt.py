# coding=utf-8

import datetime as dt
import uuid

from flask import current_app, _request_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.utils.jwt import encode_jwt, decode_jwt
from guniflask.security.authentication import BearerTokenExtractor, UserAuthentication
from guniflask.security.token import AccessToken, TokenStore, AccessTokenConverter, TokenEnhancer, \
    UserAuthenticationConverter
from guniflask.security.errors import InvalidTokenError

__all__ = ['JwtManager', 'jwt_manager']

jwt_manager = LocalProxy(lambda: current_app.extensions['jwt_manager'])


class JwtManager:
    EXP = AccessTokenConverter.EXP
    JTI = AccessTokenConverter.JTI
    AUTHORITIES = AccessTokenConverter.AUTHORITIES
    USERNAME = UserAuthenticationConverter.USERNAME
    USER_DETAILS = 'user_details'

    def __init__(self):
        self.token_extractor = BearerTokenExtractor()

    def init_app(self, app):
        self._set_default_app_config(app)
        app.extensions['jwt_manager'] = self

    def _set_default_app_config(self, app):
        app.config.setdefault('JWT_ALGORITHM', 'HS256')
        app.config.setdefault('JWT_SECRET', None)
        app.config.setdefault('JWT_PRIVATE_KEY', None)
        app.config.setdefault('JWT_PUBLIC_KEY', None)
        app.config.setdefault('ACCESS_TOKEN_EXPIRES_IN', dt.timedelta(days=1))
        app.config.setdefault('REFRESH_TOKEN_EXPIRES_IN', dt.timedelta(days=365))

    def create_access_token(self, authorities=None, username=None, user_details=None):
        config = current_app.config

        expires_in = config['ACCESS_TOKEN_EXPIRES_IN']
        payload = {
            self.JTI: str(uuid.uuid4())
        }
        exp = dt.datetime.utcnow() + expires_in
        payload[self.EXP] = exp

        payload[self.AUTHORITIES] = authorities
        payload[self.USERNAME] = username
        payload[self.USER_DETAILS] = user_details

        return encode_jwt(payload, config['JWT_SECRET'] or config['JWT_PRIVATE_KEY'],
                          config['JWT_ALGORITHM'])

    def load_authentication(self, access_token_value):
        config = current_app.config
        try:
            payload = decode_jwt(access_token_value, config['JWT_SECRET'] or config['JWT_PUBLIC_KEY'],
                                 config['JWT_ALGORITHM'])
        except Exception as e:
            raise InvalidTokenError(e)
        else:
            authorities = payload[self.AUTHORITIES]
            username = payload[self.USERNAME]
            user_details = payload[self.USER_DETAILS]
            user_auth = UserAuthentication(username, authorities=authorities)
            user_auth.details = user_details
            user_auth.authenticate(True)
        return user_auth

    def do_authentication_filter(self):
        auth = self.token_extractor.extract()
        if auth is not None:
            user_auth = self.load_authentication(auth.principal)
            ctx = _request_ctx_stack.top
            if ctx is not None:
                ctx.authentication = user_auth


class JwtTokenStore(TokenStore):
    def __init__(self):
        self.jwt_token_converter = None

    def read_authentication(self, access_token):
        if isinstance(access_token, AccessToken):
            access_token = access_token.value
        return self.jwt_token_converter.extract_authentication(self.jwt_token_converter.decode(access_token))

    def store_access_token(self, access_token, authentication):
        return None

    def read_access_token(self, access_token_value):
        access_token = self._convert_access_token(access_token_value)
        if self.jwt_token_converter.is_refresh_token(access_token):
            raise InvalidTokenError('Encoded token is a refresh token')
        return access_token

    def remove_access_token(self, access_token):
        return None

    def store_refresh_token(self, refresh_token, authentication):
        return None

    def read_refresh_token(self, refresh_token_value):
        # TODO
        pass

    def read_authentication_for_refresh_token(self, refresh_token):
        return self.read_authentication(refresh_token.value)

    def remove_refresh_token(self, refresh_token):
        return None

    def remove_access_token_using_refresh_token(self, refresh_token):
        return None

    def get_access_token(self, authentication):
        return None

    def find_tokens_by_client_id_and_username(self, client_id, username):
        return []

    def find_tokens_by_client_id(self, client_id):
        return []

    def _convert_access_token(self, access_token_value):
        return self.jwt_token_converter.extract_access_token(access_token_value,
                                                             self.jwt_token_converter.decode(access_token_value))


class JwtAccessTokenConverter(AccessTokenConverter, TokenEnhancer):
    TOKEN_ID = AccessTokenConverter.JTI
    ACCESS_TOKEN_ID = AccessTokenConverter.ATI

    def convert_access_token(self, access_token, authentication):
        # TODO
        pass

    def extract_access_token(self, token_value, data):
        # TODO
        pass

    def extract_authentication(self, data):
        # TODO
        pass

    def _enhance(self, access_token, authentication):
        # TODO
        pass

    def _encode(self, access_token, authentication):
        # TODO
        pass

    def _decode(self, token_value):
        # TODO
        pass

    def is_refresh_token(self, token):
        return self.ACCESS_TOKEN_ID in token.additional_information()
