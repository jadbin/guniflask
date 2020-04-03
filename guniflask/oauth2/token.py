# coding=utf-8

import time
import datetime as dt

__all__ = ['OAuth2AccessToken', 'OAuth2RefreshToken']


class OAuth2RefreshToken:
    """
    OAuth2 refresh token
    """

    def __init__(self, value: str, expiration: dt.datetime = None):
        self.value = value
        self.expiration = expiration

    @property
    def expires_in(self):
        if self.expiration is None:
            return 0
        return int(self.expiration.timestamp() - time.time())

    @property
    def is_expired(self):
        return self.expiration is not None and self.expires_in <= 0


class OAuth2AccessToken:
    """
    OAuth2 access token
    """

    BEARER_TYPE = 'Bearer'
    TOKEN_TYPE = 'token_type'
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'
    EXPIRES_IN = 'expires_in'
    SCOPE = 'scope'

    def __init__(self, value, refresh_token: OAuth2RefreshToken = None, expiration: dt.datetime = None, scope=None,
                 additional_information=None):
        self.value = value
        self.token_type = self.BEARER_TYPE.lower()
        self.refresh_token = refresh_token
        self.expiration = expiration
        self.scope = set()
        if scope is not None:
            self.scope.update(scope)
        self.additional_information = dict()
        if additional_information is not None:
            self.additional_information.update(additional_information)

    def __str__(self):
        return str(self.to_dict())

    @property
    def expires_in(self):
        if self.expiration is None:
            return 0
        return int(self.expiration.timestamp() - time.time())

    @property
    def is_expired(self):
        return self.expiration is not None and self.expires_in <= 0

    def to_dict(self):
        res = {self.ACCESS_TOKEN: self.value, self.TOKEN_TYPE: self.token_type}
        if self.refresh_token is not None:
            res[self.REFRESH_TOKEN] = self.refresh_token.value
        if self.expiration is not None:
            res[self.EXPIRES_IN] = self.expires_in
        if self.scope is not None:
            res[self.SCOPE] = ' '.join(self.scope)
        if self.additional_information is not None:
            res.update(self.additional_information)
        return res

    def copy(self):
        token = self.__class__(self.value,
                               refresh_token=self.refresh_token,
                               expiration=self.expiration,
                               scope=self.scope,
                               additional_information=dict(self.additional_information))
        return token
