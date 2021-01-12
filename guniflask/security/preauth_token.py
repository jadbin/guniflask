from flask import request

from guniflask.security.authentication import Authentication
from guniflask.security.authentication_token import AuthenticationToken


class PreAuthenticatedToken(AuthenticationToken):
    def __init__(self, principal, credentials=None, authorities=None):
        super().__init__(authorities=authorities)
        self._principal = principal
        self._credentials = credentials
        if authorities is not None:
            self.authenticate(True)

    @property
    def principal(self):
        return self._principal

    @property
    def credentials(self):
        return self._credentials


class BearerTokenExtractor:
    def extract(self) -> Authentication:
        token = self._extract_token_from_header()
        if token is None:
            token = self._extract_token_from_query()
        if token is not None:
            return PreAuthenticatedToken(token)

    @staticmethod
    def _extract_token_from_header():
        auth = request.headers.get('Authorization')
        if auth is not None and auth.lower().startswith('bearer'):
            return auth.split(' ', 1)[1]

    @staticmethod
    def _extract_token_from_query():
        token = request.args.get('access_token')
        if token is not None:
            return token
