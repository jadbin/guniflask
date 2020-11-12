from flask import Response


class RequestFilter:
    def before_request(self):
        pass

    def after_request(self, response: Response):
        return response


class RequestFilterChain(RequestFilter):
    def __init__(self):
        self._filters = []

    def add_request_filter(self, request_filter: RequestFilter):
        self._filters.append(request_filter)

    def before_request(self):
        for f in self._filters:
            if f.before_request:
                f.before_request()

    def after_request(self, response):
        for f in self._filters:
            if f.after_request:
                response = f.after_request(response)
        return response
