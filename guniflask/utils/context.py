from functools import update_wrapper

from flask import copy_current_request_context, current_app


def run_with_context(func):
    try:
        func = copy_current_request_context(func)
    except Exception:
        pass
    app_ctx = current_app.app_context()

    def wrapper(*args, **kwargs):
        with app_ctx:
            return func(*args, **kwargs)

    return update_wrapper(wrapper, func)
