# coding=utf-8

from flask import Response

__all__ = ['RequestFilter']


class RequestFilter:
    def before_request(self):
        pass

    def after_request(self, response: Response):
        return response
