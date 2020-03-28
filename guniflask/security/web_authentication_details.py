# coding=utf-8

from flask import request

__all__ = ['WebAuthenticationDetails']


class WebAuthenticationDetails:
    def __init__(self):
        self.remote_address = request.remote_addr
