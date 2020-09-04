# coding=utf-8

import inspect
from collections import defaultdict

from guniflask.beans.factory import BeanFactory
from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.beans.factory import BeanFactoryAware
from guniflask.annotation import AnnotationUtils
from guniflask.context.annotation import Autowired
from guniflask.beans.constructor_resolver import ConstructorResolver


class AutowiredAnnotationBeanPostProcessor(BeanPostProcessor, BeanFactoryAware):

    def __init__(self):
        self._autowired_methods = defaultdict(list)
        self._bean_factory: BeanFactory = None
        self._constructor_resolver: ConstructorResolver = None

    def set_bean_factory(self, bean_factory: BeanFactory):
        self._bean_factory = bean_factory
        self._constructor_resolver = ConstructorResolver(bean_factory)

    def post_process_before_instantiation(self, bean_type: type, bean_name: str):
        for m in dir(bean_type):
            method = getattr(bean_type, m)
            if inspect.ismethod(method) or inspect.isfunction(method):
                a = AnnotationUtils.get_annotation(method, Autowired)
                if a is not None:
                    self._autowired_methods[bean_name].append(m)

    def post_process_before_initialization(self, bean, bean_name: str):
        if bean_name in self._autowired_methods:
            for m in self._autowired_methods[bean_name]:
                if hasattr(bean, m):
                    method = getattr(bean, m)
                    self._constructor_resolver.instantiate(method)
