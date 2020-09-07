# coding=utf-8

from functools import update_wrapper

from werkzeug.exceptions import Unauthorized

from guniflask.web.user_context import current_user


def login_required(func):
    def wrapper(*args, **kwargs):
        user = current_user._get_current_object()
        if user is None:
            raise Unauthorized
        return func(*args, **kwargs)

    return update_wrapper(wrapper, func)


def has_any_role(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = current_user._get_current_object()
            if user is None or not user.has_any_role(*roles):
                raise Unauthorized
            return func(*args, **kwargs)

        return update_wrapper(wrapper, func)

    return decorator


def has_role(role):
    return has_any_role(role)


def has_any_authority(*authorities):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = current_user._get_current_object()
            if user is None or not user.has_any_authority(*authorities):
                raise Unauthorized
            return func(*args, **kwargs)

        return update_wrapper(wrapper, func)

    return decorator


def has_authority(authority):
    return has_any_authority(authority)
