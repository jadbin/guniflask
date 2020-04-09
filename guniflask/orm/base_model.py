# coding=utf-8

from typing import Union, List

import flask_sqlalchemy

from guniflask.orm.model_utils import dict_to_model, model_to_dict, update_model_by_dict, result_to_dict

__all__ = ['FeignQuery', 'BaseModelMixin']


class FeignQuery(flask_sqlalchemy.BaseQuery):

    def with_entities(self, *entities) -> 'FeignQuery':
        return super().with_entities(*entities)

    def params(self, *args, **kwargs) -> 'FeignQuery':
        return super().params(*args, **kwargs)

    def filter(self, *criterion) -> 'FeignQuery':
        return super().filter(*criterion)

    def filter_by(self, **kwargs) -> 'FeignQuery':
        return super().filter_by(**kwargs)

    def order_by(self, *criterion) -> 'FeignQuery':
        return super().order_by(*criterion)

    def group_by(self, *criterion) -> 'FeignQuery':
        return super().group_by(*criterion)

    def having(self, criterion) -> 'FeignQuery':
        return super().having(criterion)

    def union(self, *q) -> 'FeignQuery':
        return super().union(*q)

    def union_all(self, *q) -> 'FeignQuery':
        return super().union_all(*q)

    def intersect(self, *q) -> 'FeignQuery':
        return super().intersect(*q)

    def intersect_all(self, *q) -> 'FeignQuery':
        return super().intersect_all(*q)

    def except_(self, *q) -> 'FeignQuery':
        return super().except_(*q)

    def except_all(self, *q) -> 'FeignQuery':
        return super().except_all(*q)

    def join(self, *props, **kwargs) -> 'FeignQuery':
        return super().join(*props, **kwargs)

    def outerjoin(self, *props, **kwargs) -> 'FeignQuery':
        return super().outerjoin(*props, **kwargs)

    def reset_joinpoint(self) -> 'FeignQuery':
        return super().reset_joinpoint()

    def select_from(self, *from_obj) -> 'FeignQuery':
        return super().select_from(*from_obj)

    def select_entity_from(self, from_obj) -> 'FeignQuery':
        return super().select_entity_from(from_obj)

    def slice(self, start, stop) -> 'FeignQuery':
        return super().slice(start, stop)

    def limit(self, limit) -> 'FeignQuery':
        return super().limit(limit)

    def offset(self, offset) -> 'FeignQuery':
        return super().offset(offset)

    def distinct(self, *expr) -> 'FeignQuery':
        return super().distinct(*expr)

    def prefix_with(self, *prefixes) -> 'FeignQuery':
        return super().prefix_with(*prefixes)

    def suffix_with(self, *suffixes) -> 'FeignQuery':
        return super().suffix_with(*suffixes)


class BaseModelMixin:
    query: FeignQuery

    @classmethod
    def from_dict(cls, dict_obj: dict,
                  ignore: Union[str, List] = None,
                  only: Union[str, List] = None,
                  only_not_none: bool = False):
        return dict_to_model(dict_obj, cls, ignore=ignore, only=only, only_not_none=only_not_none)

    def to_dict(self, ignore: Union[str, List] = None,
                only: Union[str, List] = None,
                only_not_none: bool = False):
        return model_to_dict(self, ignore=ignore, only=only, only_not_none=only_not_none)

    def update_by_dict(self, dict_obj: dict,
                       ignore: Union[str, List] = None,
                       only: Union[str, List] = None,
                       only_not_none: bool = False):
        return update_model_by_dict(self, dict_obj, ignore=ignore, only=only, only_not_none=only_not_none)

    @classmethod
    def result_to_dict(cls, result,
                       ignore: Union[str, List] = None,
                       only: Union[str, List] = None,
                       only_not_none: bool = False):
        return result_to_dict(result, cls, ignore=ignore, only=only, only_not_none=only_not_none)
