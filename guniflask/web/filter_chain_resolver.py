# coding=utf-8

from typing import List

from guniflask.web.request_filter import RequestFilter
from guniflask.beans.constructor_resolver import ConstructorResolver
from guniflask.beans.factory import BeanFactory


class FilterChainResolver:
    def __init__(self, bean_factory: BeanFactory):
        self._constructor_resolver = ConstructorResolver(bean_factory)

    def register_request_filters(self, app, values):
        request_filters = self._resolve_request_filters(values)
        for f in request_filters:
            d = set(type(f).__dict__.keys())
            if 'before_request' in d:
                app.before_request(f.before_request)
            if 'after_request' in d:
                app.after_request(f.after_request)

    def _resolve_request_filters(self, values) -> List[RequestFilter]:
        result = []
        for v in values:
            if isinstance(v, RequestFilter):
                result.append(v)
            else:
                f = self._constructor_resolver.instantiate(v)
                assert isinstance(f, RequestFilter), 'Required a request filter, ' \
                                                     'got: {}'.format(type(RequestFilter).__name__)
        return result
