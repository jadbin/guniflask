from guniflask.web import blueprint, get_route


@blueprint
class GzipController:
    @get_route('/gzip/json-512')
    def get_json_512(self):
        return {
            'result': 'a' * 512
        }

    @get_route('/gzip/json-1024')
    def get_json_1024(self):
        return {
            'result': 'a' * 1024
        }
