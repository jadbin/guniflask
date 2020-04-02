# coding=utf-8

from guniflask.web.request_filter import RequestFilter, RequestFilterMetadata

__all__ = ['SecurityFilterChain']


class SecurityFilterChain(RequestFilter):
    def __init__(self):
        self._filters = []

    def add_request_filter(self, request_filter: RequestFilter):
        request_filter.metadata = RequestFilterMetadata(request_filter)
        self._filters.append(request_filter)

    def before_request(self):
        for f in self._filters:
            if f.metadata.before_request:
                f.metadata.before_request()

    def after_request(self, response):
        for f in self._filters:
            if f.metadata.after_request:
                response = f.metadata.after_request(response)
        return response
