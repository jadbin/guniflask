# coding=utf-8

from flask import g

from guniflask.web.request_filter import RequestFilter
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.oauth2.token_extractor import TokenExtractor, BearerTokenExtractor
from guniflask.security.context import SecurityContext
from guniflask.oauth2.authentication_details import OAuth2AuthenticationDetails
from guniflask.security.authentication_token import AuthenticationToken


class OAuth2AuthenticationFilter(RequestFilter):
    def __init__(self, authentication_manager: AuthenticationManager):
        self.authentication_manager = authentication_manager
        self.token_extractor: TokenExtractor = BearerTokenExtractor()

    def before_request(self):
        authentication = self.token_extractor.extract()
        if authentication:
            g.setdefault(OAuth2AuthenticationDetails.ACCESS_TOKEN_VALUE, authentication.principal)
            if isinstance(authentication, AuthenticationToken):
                authentication.details = OAuth2AuthenticationDetails()
            auth_result = self.authentication_manager.authenticate(authentication)
            SecurityContext.set_authentication(auth_result)
