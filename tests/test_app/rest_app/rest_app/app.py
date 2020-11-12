import logging

from flask import Flask
from guniflask.config import Settings
from guniflask.context import AnnotationConfigBeanContext

log = logging.getLogger(__name__)


def make_settings(app: Flask, settings: Settings):
    pass


def init_app(app: Flask, settings: Settings):
    test_bean_context()


def test_bean_context():
    bean_context = AnnotationConfigBeanContext()
    bean_context.scan('rest_app.lifecycle_component')
    bean_context.refresh()
    bean_context.close()
