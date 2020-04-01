# coding=utf-8

from flask import request, g

__all__ = ['OAuth2AuthenticationDetails']


class OAuth2AuthenticationDetails:
    ACCESS_TOKEN_VALUE = __qualname__ + '.access_token_value'
    ACCESS_TOKEN_TYPE = __qualname__ + '.access_token_type'

    def __init__(self):
        self.remote_address = request.remote_addr
        self.token_type = g.get(self.ACCESS_TOKEN_TYPE)
        self.token_value = g.get(self.ACCESS_TOKEN_VALUE)
