from typing import Union

from guniflask.config import settings
from guniflask.security import JwtManager, SecurityContext, BearerTokenExtractor
from guniflask.security_config import SecurityConfigurer, HttpSecurityBuilder
from guniflask.web import RequestFilter
from werkzeug.local import LocalProxy

jwt_manager: Union[JwtManager, LocalProxy] = LocalProxy(lambda: settings['_jwt_manager'])


class JwtConfigurer(SecurityConfigurer):
    def __init__(self):
        super().__init__()
        jwt = settings.get_by_prefix('guniflask.jwt')
        if jwt:
            self.active = True
            settings['_jwt_manager'] = JwtManager(**jwt)
        else:
            self.active = False

    def configure(self, http: HttpSecurityBuilder):
        if self.active:
            http.add_request_filter(JwtFilter())


class JwtFilter(RequestFilter):
    def __init__(self):
        self.token_extractor = BearerTokenExtractor()

    def before_request(self):
        auth = self.token_extractor.extract()
        if auth is not None:
            user_auth = jwt_manager.authenticate(auth)
            SecurityContext.set_authentication(user_auth)
