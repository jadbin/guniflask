# coding=utf-8

__all__ = ['RequestFilter']


class RequestFilter:
    def before_request(self):
        pass

    def after_request(self, response):
        return response
