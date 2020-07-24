# coding=utf-8

from typing import Union, List

from guniflask.orm.model_utils import dict_to_model, model_to_dict, update_model_by_dict, result_to_dict

__all__ = ['BaseModelMixin']


class BaseModelMixin:

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
