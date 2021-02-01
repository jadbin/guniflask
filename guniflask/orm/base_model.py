from typing import Union, List, Set

from sqlalchemy.orm import Query

from guniflask.orm.model_utils import dict_to_model, model_to_dict, update_model_by_dict


class BaseModelMixin:
    query: Query

    @classmethod
    def from_dict(
            cls,
            dict_obj: dict,
            ignore: Union[str, List[str], Set[str]] = None,
            only: Union[str, List[str], Set[str]] = None,
    ):
        return dict_to_model(dict_obj, cls, ignore=ignore, only=only)

    def to_dict(
            self,
            ignore: Union[str, List[str], Set[str]] = None,
            only: Union[str, List[str], Set[str]] = None,
            include: Union[str, List[str], Set[str]] = None,
    ):
        return model_to_dict(self, ignore=ignore, only=only, include=include)

    def update_by_dict(
            self,
            dict_obj: dict,
            ignore: Union[str, List[str], Set[str]] = None,
            only: Union[str, List[str], Set[str]] = None,
    ):
        return update_model_by_dict(self, dict_obj, ignore=ignore, only=only)
