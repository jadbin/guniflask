# coding=utf-8

import base64

from flask import request

from guniflask.web.request_filter import RequestFilter
from guniflask.security.authentication_manager import AuthenticationManager
from guniflask.security.context import SecurityContext
from guniflask.security.authentication_token import UserAuthentication
from guniflask.security.web_authentication_details import WebAuthenticationDetails
from guniflask.security.errors import BadCredentialsError

__all__ = ['BasicAuthenticationFilter']


class BasicAuthenticationFilter(RequestFilter):
    def __init__(self, authentication_manger: AuthenticationManager):
        self.authentication_manager = authentication_manger

    def before_request(self):
        header = request.headers.get('Authorization')
        if header is None or not header.startswith('Basic '):
            return
        username, password = self._extract_from_header(header)
        if self._require_authentication(username):
            auth_request = UserAuthentication(username, credentials=password)
            auth_request.details = WebAuthenticationDetails()
            auth_result = self.authentication_manager.authenticate(auth_request)
            SecurityContext.set_authentication(auth_result)

    def _extract_from_header(self, header: str):
        header = header[6:].encode('utf-8')
        decoded = base64.b64decode(header)
        token = decoded.decode('utf-8')
        s = token.split(':', maxsplit=1)
        if len(s) < 2:
            raise BadCredentialsError('Invalid basic authentication token')
        return s[0], s[1]

    def _require_authentication(self, username: str) -> bool:
        existing_auth = SecurityContext.get_authentication()
        if existing_auth is None or not existing_auth.is_authenticated:
            return True
        if isinstance(existing_auth, UserAuthentication) and existing_auth.name != username:
            return True
        return False
