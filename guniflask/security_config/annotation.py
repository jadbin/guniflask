# coding=utf-8

from guniflask.annotation import AnnotationUtils
from guniflask.context.annotation import Include
from guniflask.security_config.web_security_config import WebSecurityConfiguration
from guniflask.security_config.authentication_config import AuthenticationConfiguration


def enable_authentication(func):
    values = [AuthenticationConfiguration]
    AnnotationUtils.add_annotation(func, Include(values))
    return func


def enable_web_security(func):
    values = [WebSecurityConfiguration,
              AuthenticationConfiguration]
    AnnotationUtils.add_annotation(func, Include(values))
    return func
