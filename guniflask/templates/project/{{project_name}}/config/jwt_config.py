# coding=utf-8

from flask import current_app

from guniflask.context import configuration
from guniflask.beans import SmartInitializingSingleton
from guniflask.security import JwtManager, SecurityContext
from guniflask.config import settings
from guniflask.web import RequestFilter
from guniflask.oauth2 import BearerTokenExtractor


@configuration
class JwtConfiguration(SmartInitializingSingleton):

    def after_singletons_instantiated(self):
        self.configure_jwt()

    def configure_jwt(self):
        jwt_config = settings.get_by_prefix('guniflask.jwt')
        if jwt_config and isinstance(jwt_config, dict):
            jwt_manager = JwtManager(**jwt_config)
            jwt_filter = JwtFilter(jwt_manager)
            current_app.before_request(jwt_filter.before_request)


class JwtFilter(RequestFilter):
    def __init__(self, jwt_manager: JwtManager):
        self.jwt_manager = jwt_manager
        self.token_extractor = BearerTokenExtractor()

    def before_request(self):
        auth = self.token_extractor.extract()
        if auth is not None:
            user_auth = self.jwt_manager.authenticate(auth)
            SecurityContext.set_authentication(user_auth)
