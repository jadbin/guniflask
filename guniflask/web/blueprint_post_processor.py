# coding=utf-8

from flask import Flask, Blueprint as FlaskBlueprint

from guniflask.annotation.annotation_utils import AnnotationUtils
from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.web.bind_annotation import Blueprint, Route

__all__ = ['BlueprintPostProcessor']


class BlueprintPostProcessor(BeanPostProcessor):
    BLUEPRINT = '__blueprint'

    def __init__(self, app: Flask):
        self.app = app

    def post_process_after_initialization(self, bean, bean_name: str):
        bean_type = bean.__class__
        annotation = AnnotationUtils.get_annotation(bean_type, Blueprint)
        if annotation is not None:
            if not hasattr(bean, self.BLUEPRINT):
                options = annotation['options'] or {}
                b = FlaskBlueprint(bean_name, bean.__module__,
                                   url_prefix=annotation['url_prefix'], **options)
                for m in dir(bean):
                    method = getattr(bean, m)
                    a = AnnotationUtils.get_annotation(method, Route)
                    if a is not None:
                        rule_options = a['options'] or {}
                        b.add_url_rule(a['rule'], endpoint=method.__name__, view_func=method, **rule_options)
                self.app.register_blueprint(b)
        return bean
