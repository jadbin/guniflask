# coding=utf-8

from guniflask.annotation.annotation_utils import AnnotationUtils
from guniflask.context.annotation import Include
from guniflask.oauth2_config.authorization_server_endpoints import AuthorizationServerEndpointsConfiguration
from guniflask.oauth2_config.client_details_service import ClientDetailsServiceConfiguration
from guniflask.oauth2_config.resource_server import ResourceServerConfiguration

__all__ = ['enable_authorization_server',
           'enable_resource_server']


def enable_authorization_server(func):
    values = [AuthorizationServerEndpointsConfiguration,
              ClientDetailsServiceConfiguration]
    AnnotationUtils.add_annotation(func, Include(values))
    return func


def enable_resource_server(func):
    values = [ResourceServerConfiguration]
    AnnotationUtils.add_annotation(func, Include(values))
    return func
