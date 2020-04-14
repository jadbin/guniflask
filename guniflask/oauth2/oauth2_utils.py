# coding=utf-8

import re
from typing import Optional, Dict

from flask import request

__all__ = ['OAuth2Utils']


class OAuth2Utils:
    CLIENT_ID = 'client_id'
    STATE = 'state'
    SCOPE = 'scope'
    REDIRECT_URI = 'redirect_uri'
    RESPONSE_TYPE = 'response_type'
    USER_OAUTH_APPROVAL = 'user_oauth_approval'
    SCOPE_PREFIX = 'scope.'
    GRANT_TYPE = 'grant_type'

    @staticmethod
    def parse_parameter_list(values: str) -> set:
        result = set()
        if values is not None:
            values = values.strip()
            if values:
                s = re.split(r'\s+', values)
                result.update(s)
        return result

    @staticmethod
    def format_parameter_list(value: set) -> Optional[str]:
        if not value:
            return None
        return ' '.join(value)

    @staticmethod
    def get_request_parameters() -> Dict[str, str]:
        result = {}
        for k in request.args:
            result[k] = request.args.get(k)
        return result
