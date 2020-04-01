# coding=utf-8

from abc import ABCMeta, abstractmethod

from flask import request, g

from guniflask.security.authentication import Authentication
from guniflask.security.preauth_token import PreAuthenticatedToken
from guniflask.oauth2.token import OAuth2AccessToken
from guniflask.oauth2.authentication_details import OAuth2AuthenticationDetails

__all__ = ['TokenExtractor', 'BearerTokenExtractor']


class TokenExtractor(metaclass=ABCMeta):
    @abstractmethod
    def extract(self) -> Authentication:
        pass


class BearerTokenExtractor(TokenExtractor):
    def extract(self) -> Authentication:
        token = self._extract_token_from_header()
        if token is None:
            token = self._extract_token_from_query()
        if token is not None:
            return PreAuthenticatedToken(token)

    @staticmethod
    def _extract_token_from_header():
        auth = request.headers.get('Authorization')
        if auth is not None and auth.lower().startswith(OAuth2AccessToken.BEARER_TYPE.lower()):
            g.setdefault(OAuth2AuthenticationDetails.ACCESS_TOKEN_TYPE, OAuth2AccessToken.BEARER_TYPE)
            return auth.split(' ', 1)[1]

    @staticmethod
    def _extract_token_from_query():
        token = request.args.get(OAuth2AccessToken.ACCESS_TOKEN)
        if token is not None:
            g.setdefault(OAuth2AuthenticationDetails.ACCESS_TOKEN_TYPE, OAuth2AccessToken.BEARER_TYPE)
