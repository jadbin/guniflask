from contextlib import contextmanager

from guniflask.app.factory import create_app
from guniflask.test.env import set_test_env


@contextmanager
def app_test_client():
    set_test_env()
    app = create_app()
    with app.app_context():
        with app.test_client() as client:
            yield client
