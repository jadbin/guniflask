# coding=utf-8

import json
from os.path import join
from functools import wraps

from flask import request, abort, jsonify, render_template, current_app

from guniflask.utils.template import template_folder
from guniflask.config import settings
from guniflask.security import roles_required
from guniflask.web import blueprint, get_route, route

static_folder = join(template_folder, 'static')


def debug_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if settings['debug']:
            return func(*args, **kwargs)
        return render_template('debug_only.html'), 403

    return wrapper


accounts = {
    'root': {
        'password': '123456',
        'authorities': ['role_admin', 'role_user']
    }
}


@blueprint(url_prefix='/hello-world',
           template_folder=join(template_folder, 'hello_world'),
           static_folder=static_folder,
           static_url_path='/static')
class HelloWorld:
    """
    An example
    """

    def __init__(self):
        self.jwt_manager = current_app.extensions['jwt_manager']

    @get_route('/')
    def home_page(self):
        """
        Home page
        """
        return render_template('index.html')

    @route('/login', methods=['GET', 'POST'])
    def login(self):
        """
        Login app
        """
        if request.method == 'GET':
            return render_template('login.html')
        data = request.get_json()
        if data is not None:
            username = data.get('username')
            password = data.get('password')
            if username in accounts and password == accounts[username]['password']:
                token = self.jwt_manager.create_access_token(accounts[username]['authorities'],
                                                             username=username)
                return jsonify({'access_token': token,
                                'username': username})
        return abort(403)

    @get_route('/settings')
    @debug_only
    def get_settings(self):
        """
        Settings page
        """
        return render_template('settings.html')

    @get_route('/settings-table')
    @roles_required('admin')
    def get_settings_table(self):
        """
        Get settings of app
        """
        s = {}
        for k, v in settings.items():
            if is_jsonable(v):
                s[k] = v
        app_settings = [{'key': i, 'value': j} for i, j in s.items()]
        app_settings.sort(key=lambda k: k['key'])
        return render_template('settings_table.html', app_settings=app_settings)


def is_jsonable(v):
    try:
        json.dumps(v)
    except Exception:
        return False
    return True
