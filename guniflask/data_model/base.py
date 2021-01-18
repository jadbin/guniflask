from enum import Enum
from typing import get_type_hints, Any, Union, List

from guniflask.data_model.typing import parse_json
from guniflask.orm.base_model import BaseModelMixin


class DataModel:
    def __init__(self, **data: Any):
        cls = self.__class__
        for k in get_type_hints(cls):
            if k in data:
                setattr(self, k, data[k])
            elif not hasattr(self, k):
                setattr(self, k, None)

    def to_dict(self) -> dict:
        cls = self.__class__
        d = {}
        for k in get_type_hints(cls):
            d[k] = self._get_value(getattr(self, k, None))
        return d

    def _get_value(self, v: Any) -> Any:
        if isinstance(v, DataModel):
            return v.to_dict()
        if isinstance(v, dict):
            return {_k: self._get_value(_v) for _k, _v in v.items()}
        if isinstance(v, (list, set, tuple)):
            return [self._get_value(_v) for _v in v]
        if isinstance(v, Enum):
            return v.value
        return v

    @classmethod
    def from_dict(cls, obj: dict) -> 'DataModel':
        return parse_json(obj, cls)

    @classmethod
    def from_orm(
            cls,
            obj: BaseModelMixin,
            ignore: Union[str, List] = None,
            only: Union[str, List] = None,
            include: Union[str, List] = None,
    ) -> 'DataModel':
        return cls.from_dict(
            obj.to_dict(
                ignore=ignore,
                only=only,
                include=include,
            )
        )
