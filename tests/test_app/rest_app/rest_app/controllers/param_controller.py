from flask import jsonify

from guniflask.web import blueprint, post_route, RequestBody, get_route, FormValue, FilePart, CookieValue, RequestHeader


@blueprint
class ParamController:
    @get_route('/get/int')
    def get_int(self, x: int):
        return {'x': x}

    @get_route('/get/str')
    def get_str(self, x: str):
        return {'x': x}

    @get_route('/get/default')
    def get_default(self, x: str = 'default'):
        return {'x': x}

    @post_route('/post/dict')
    def post_dict(self, data: dict = RequestBody):
        assert isinstance(data, dict), type(data)
        return data

    @post_route('/post/list')
    def post_list(self, data: list = RequestBody):
        assert isinstance(data, list), type(data)
        return jsonify(data)

    @post_route('/post/form-int')
    def post_form_int(self, x: int = FormValue):
        return {'x': x}

    @post_route('/post/form-str')
    def post_form_str(self, x: str = FormValue):
        return {'x': x}

    @post_route('/post/file-bytes')
    def post_file_bytes(self, x: bytes = FilePart):
        assert isinstance(x, bytes)
        return {'x': x.decode()}

    @post_route('/post/cookie-str')
    def post_cookie_str(self, x: str = CookieValue):
        return {'x': x}

    @post_route('/post/cookie-int')
    def post_cookie_int(self, x: int = CookieValue):
        return {'x': x}

    @post_route('/post/header-int')
    def post_header_int(self, x: int = RequestHeader):
        return {'x': x}

    @post_route('/post/header-str')
    def post_header_str(self, x: str = RequestHeader):
        return {'x': x}
