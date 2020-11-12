from functools import update_wrapper

from flask import _request_ctx_stack, copy_current_request_context, current_app


def run_with_context(func):
    if _request_ctx_stack.top is not None:
        func = copy_current_request_context(func)
    app_ctx = current_app.app_context()

    def wrapper(*args, **kwargs):
        with app_ctx:
            return func(*args, **kwargs)

    return update_wrapper(wrapper, func)
