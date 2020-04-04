# coding=utf-8


__all__ = ['ConsulError',
           'ConsulClientError']


class ConsulError(Exception):
    pass


class ConsulClientError(ConsulError):
    pass
