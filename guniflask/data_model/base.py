# coding=utf-8

from typing import get_type_hints, Any

from guniflask.data_model.mapping import map_json
from guniflask.orm.base_model import BaseModelMixin


class DataModel:
    def __init__(self, **data: Any):
        cls = self.__class__
        for k in get_type_hints(cls):
            if k in data:
                setattr(self, k, data[k])
            elif not hasattr(self, k):
                setattr(self, k, None)

    def to_dict(self):
        cls = self.__class__
        d = {}
        for k in get_type_hints(cls):
            d[k] = getattr(self, k, None)
        return d

    @classmethod
    def from_dict(cls, obj: dict):
        return map_json(obj, cls)

    @classmethod
    def from_orm(cls, obj: BaseModelMixin):
        return cls.from_dict(obj.to_dict())
