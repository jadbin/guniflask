# coding=utf-8

from typing import List

from guniflask.web.request_filter import RequestFilter, RequestFilterChain
from guniflask.beans.constructor_resolver import ConstructorResolver
from guniflask.beans.factory import BeanFactory
from guniflask.annotation.core import AnnotationUtils
from guniflask.web.filter_annotation import FilterChain

__all__ = ['FilterChainResolver']


class FilterChainResolver:
    def __init__(self, bean_factory: BeanFactory):
        self._constructor_resolver = ConstructorResolver(bean_factory)
        self._blueprints = []

    def add_blueprint(self, blueprint, bean_type):
        self._blueprints.append((blueprint, bean_type))

    def build(self):
        for b, bean_type in self._blueprints:
            filter_chain_annotation = AnnotationUtils.get_annotation(bean_type, FilterChain)
            if filter_chain_annotation is not None:
                request_filters = self._resolve_request_filters(filter_chain_annotation['values'])
                if request_filters:
                    chain = RequestFilterChain()
                    for f in request_filters:
                        chain.add_request_filter(f)
                    b.before_request(chain.before_request)
                    b.after_request(chain.after_request)

    def _resolve_request_filters(self, values) -> List[RequestFilter]:
        if not hasattr(values, '__iter__'):
            values = [values]
        result = []
        for v in values:
            if isinstance(v, RequestFilter):
                result.append(v)
            else:
                f = self._constructor_resolver.instantiate(v)
                assert isinstance(f, RequestFilter), 'Required a request filter, ' \
                                                     'got: {}'.format(type(RequestFilter).__name__)
        return result
