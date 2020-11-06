# coding=utf-8

from guniflask.context import service


@service
class MathService:
    def add(self, x, y):
        return x + y
