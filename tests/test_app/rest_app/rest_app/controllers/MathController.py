# coding=utf-8

from guniflask.web import blueprint, get_route

from ..services.math_service import MathService


@blueprint('/api')
class MathController:
    def __init__(self, math_service: MathService):
        self.math_service = math_service

    @get_route('/math/add')
    def add(self, x: float, y: float):
        return {'result': self.math_service.add(x, y)}
