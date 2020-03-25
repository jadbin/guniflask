# coding=utf-8

from guniflask.annotation.annotation_utils import AnnotationUtils
from guniflask.context.annotation import Include
from guniflask.oauth2_config.authorization_server_endpoints import AuthorizationServerEndpointsConfiguration

__all__ = ['enable_authorization_server']


def enable_authorization_server():
    def wrap_func(func):
        values = [AuthorizationServerEndpointsConfiguration]
        AnnotationUtils.add_annotation(func, Include(values))
        return func

    return wrap_func
