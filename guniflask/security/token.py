# coding=utf-8

from datetime import datetime

__all__ = ['OAuth2AccessToken', 'OAuth2RefreshToken']


class OAuth2RefreshToken:
    """
    OAuth2 refresh token
    """

    def __init__(self, value: str, expiration: datetime = None):
        self.value = value
        self.expiration = expiration


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

    def __init__(self, value, refresh_token: OAuth2RefreshToken = None, expiration: datetime = None, scope=None,
                 additional_info=None):
        self.value = value
        self.token_type = self.BEARER_TYPE.lower()
        self.refresh_token = refresh_token
        self.expiration = expiration
        self.scope = set()
        if scope is not None:
            self.scope.update(scope)
        self.additional_info = dict()
        if additional_info is not None:
            self.additional_info.update(additional_info)

    def __str__(self):
        return str(self.to_dict())

    @property
    def expires_in(self):
        if self.expiration is None:
            return 0
        return int(self.expiration.timestamp() - datetime.now().timestamp())

    def to_dict(self):
        res = {self.ACCESS_TOKEN: self.value, self.TOKEN_TYPE: self.token_type}
        if self.refresh_token is not None:
            res[self.REFRESH_TOKEN] = self.refresh_token.value
        if self.expiration is not None:
            res[self.EXPIRES_IN] = self.expires_in
        if self.scope is not None:
            res[self.SCOPE] = ' '.join(self.scope)
        if self.additional_info is not None:
            res.update(self.additional_info)
        return res
