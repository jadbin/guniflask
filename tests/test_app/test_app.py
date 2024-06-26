import gzip
import io
import json
import os
import time
from os.path import dirname, abspath, join

import pytest
from flask.testing import FlaskClient

from guniflask.test import app_test_client


@pytest.fixture
def rest_client():
    os.environ['GUNIFLASK_HOME'] = join(dirname(abspath(__file__)), 'rest_app')
    with app_test_client() as client:
        client.application.config['TESTING'] = True
        yield client
        clear_env()


@pytest.fixture
def scheduler_client():
    os.environ['GUNIFLASK_HOME'] = join(dirname(abspath(__file__)), 'scheduler_app')
    with app_test_client() as client:
        client.application.config['TESTING'] = True
        yield client
        clear_env()


def clear_env():
    for k in os.environ:
        if k.startswith('GUNIFLASK_'):
            os.environ.pop(k)


def get_json(resp):
    assert resp.status_code == 200
    if resp.headers.get('Content-Encoding') == 'gzip':
        resp.set_data(gzip.decompress(resp.data))
    return resp.get_json()


class TestRestApp:
    def test_get_default_setting(self, rest_client: FlaskClient):
        data = get_json(rest_client.get('/settings/app_name'))
        assert data['app_name'] == 'rest_app'

        data = get_json(rest_client.get('/settings/debug'))
        assert data['debug'] is True

    def test_math_service(self, rest_client: FlaskClient):
        data = get_json(rest_client.get('/api/math/add?x=1&y=2'))
        assert data['result'] == 3

    def test_query_param(self, rest_client: FlaskClient):
        data = get_json(rest_client.get('/get/int?x=1'))
        assert data['x'] == 1

        data = get_json(rest_client.get('/get/str?x=1'))
        assert data['x'] == '1'

        data = get_json(rest_client.get('/get/default'))
        assert data['x'] == 'default'

    def test_post_dict(self, rest_client: FlaskClient):
        data = get_json(
            rest_client.post(
                '/post/dict',
                json=dict(
                    a=1,
                    b='1',
                ),
            )
        )
        assert data['a'] == 1
        assert data['b'] == '1'

    def test_post_list(self, rest_client: FlaskClient):
        data = get_json(
            rest_client.post(
                '/post/list',
                data=json.dumps([1, '1']),
                content_type='application/json',
            )
        )
        assert data == [1, '1']

    def test_post_form(self, rest_client: FlaskClient):
        data = get_json(
            rest_client.post(
                '/post/form-int',
                data='x=1',
                content_type='application/x-www-form-urlencoded',
            )
        )
        assert data == {'x': 1}

        data = get_json(
            rest_client.post(
                '/post/form-str',
                data='x=1',
                content_type='application/x-www-form-urlencoded',
            )
        )
        assert data == {'x': '1'}

    def test_post_file(self, rest_client: FlaskClient):
        data = get_json(
            rest_client.post(
                '/post/file-bytes',
                data={
                    'x': (io.BytesIO(b'file'), 'test.txt')
                },
                content_type='multipart/form-data',
            )
        )
        assert data['x'] == 'file'

    def test_post_cookie(self, rest_client: FlaskClient):
        rest_client.set_cookie(domain='localhost', key='x', value='1')
        data = get_json(
            rest_client.post(
                '/post/cookie-int',
            )
        )
        assert data['x'] == 1

        data = get_json(
            rest_client.post(
                '/post/cookie-str',
            )
        )
        assert data['x'] == '1'

    def test_post_header(self, rest_client: FlaskClient):
        rest_client.set_cookie(domain='localhost', key='x', value='1')
        data = get_json(
            rest_client.post(
                '/post/header-int',
                headers={'x': '1'},
            )
        )
        assert data['x'] == 1

        data = get_json(
            rest_client.post(
                '/post/header-str',
                headers={'x': '1'},
            )
        )
        assert data['x'] == '1'

    def test_login(self, rest_client: FlaskClient):
        data = get_json(
            rest_client.post(
                '/login?username=root&password=123456',
            )
        )
        assert data['username'] == 'root'
        assert 'access_token' in data
        token = data['access_token']

        data = get_json(
            rest_client.get(
                '/accounts/account-info',
                headers={'Authorization': 'Bearer ' + token},
            )
        )
        assert data['username'] == 'root'
        assert data['authorities'] == ['role_admin']

        data = get_json(
            rest_client.get(
                '/accounts/account-info-gevent',
                headers={'Authorization': 'Bearer ' + token},
            )
        )
        assert data['username'] == 'root'
        assert data['authorities'] == ['role_admin']

    def test_gzip(self, rest_client: FlaskClient):
        resp = rest_client.get(
            '/gzip/json-512',
        )
        assert 'Content-Encoding' not in resp.headers
        data = get_json(resp)
        assert len(data['result']) == 512

        resp = rest_client.get(
            '/gzip/json-1024',
        )
        assert resp.headers.get('Content-Encoding') == 'gzip'
        data = get_json(resp)
        assert len(data['result']) == 1024


class TestSchedulerApp:
    def test_schedule_task(self, scheduler_client: FlaskClient):
        scheduler_client.post('/async-add?x=1&y=2')
        time.sleep(2)
        data = get_json(scheduler_client.get('/scheduled'))
        assert data['result'] is True
        data = get_json(scheduler_client.get('/async-add'))
        assert data['result'] == 3
