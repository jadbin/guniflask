# coding=utf-8

from guniflask.annotation.core import AnnotationUtils
from guniflask.context.annotation import Include
from guniflask.oauth2_config.authorization_server_config import AuthorizationServerEndpointsConfiguration, \
    AuthorizationServerSecurityConfiguration
from guniflask.oauth2_config.resource_server_config import ResourceServerConfiguration

__all__ = ['enable_authorization_server',
           'enable_resource_server']


def enable_authorization_server(func):
    values = [AuthorizationServerEndpointsConfiguration,
              AuthorizationServerSecurityConfiguration]
    AnnotationUtils.add_annotation(func, Include(values))
    return func


def enable_resource_server(func):
    values = [ResourceServerConfiguration]
    AnnotationUtils.add_annotation(func, Include(values))
    return func
