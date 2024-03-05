from guniflask.security_config.http_security_builder import HttpSecurityBuilder
from guniflask.security_config.security_configurer import SecurityConfigurer
from guniflask.web.cors import CorsFilter


class CorsConfigurer(SecurityConfigurer):

    def __init__(self, options=None):
        super().__init__()

        if isinstance(options, dict):
            self.cors_filter = CorsFilter(**options)
        else:
            self.cors_filter = CorsFilter()

    def configure(self, http: HttpSecurityBuilder):
        http.add_request_filter(self.cors_filter)
