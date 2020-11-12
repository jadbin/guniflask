from guniflask.config import settings
from guniflask.web import blueprint, get_route


@blueprint
class ConfigController:
    def __init__(self):
        pass

    @get_route('/settings/<name>')
    def get_setting(self, name):
        return {name: settings[name]}
