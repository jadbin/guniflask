# coding=utf-8

from typing import List

from guniflask.web.request_filter import RequestFilter, RequestFilterMetadata
from guniflask.beans.constructor_resolver import ConstructorResolver
from guniflask.beans.factory import BeanFactory

__all__ = ['FilterChainResolver']


class FilterChainResolver:
    def __init__(self, bean_factory: BeanFactory):
        self._constructor_resolver = ConstructorResolver(bean_factory)

    def register_request_filters(self, app, values):
        request_filters = self._resolve_request_filters(values)
        for f in request_filters:
            m = RequestFilterMetadata(f)
            if m.before_request:
                app.before_request(m.before_request)
            if m.after_request:
                app.after_request(m.after_request)

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
