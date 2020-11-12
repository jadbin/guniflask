from guniflask.scheduling import scheduled, async_run
from guniflask.web import blueprint, post_route, get_route


@blueprint
class SchedulerController:

    def __init__(self):
        self.scheduled = False
        self.async_result = None

    @scheduled(interval=1)
    def schedule_task(self):
        self.scheduled = True

    @get_route('/scheduled')
    def get_scheduled(self):
        return {'result': self.scheduled}

    @post_route('/async-add')
    def async_add(self, x: float, y: float):
        self.do_async_add(x, y)
        return {}

    @async_run
    def do_async_add(self, x: float, y: float):
        self.async_result = x + y

    @get_route('/async-add')
    def get_async_add_result(self):
        return {'result': self.async_result}
