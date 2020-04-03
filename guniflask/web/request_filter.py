# coding=utf-8

from flask import Response

__all__ = ['RequestFilter', 'RequestFilterMetadata', 'RequestFilterChain']


class RequestFilter:
    def before_request(self):
        pass

    def after_request(self, response: Response):
        return response


class RequestFilterMetadata:
    def __init__(self, request_filter: RequestFilter):
        self.before_request = None
        self.after_request = None
        d = set(type(request_filter).__dict__.keys())
        if 'before_request' in d:
            self.before_request = request_filter.before_request
        if 'after_request' in d:
            self.after_request = request_filter.after_request


class RequestFilterChain(RequestFilter):
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
