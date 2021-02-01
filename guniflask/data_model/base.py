from enum import Enum
from typing import Union, List, Set, Any

from pydantic import BaseModel

from guniflask.orm.base_model import BaseModelMixin
from guniflask.utils.rule import make_ignore_rule_for_field, make_only_rule_for_field


class DataModel(BaseModel):
    def to_dict(
            self,
            ignore: Union[str, List[str], Set[str]] = None,
            only: Union[str, List[str], Set[str]] = None,
    ) -> dict:
        ignore = make_ignore_rule_for_field(ignore)
        only = make_only_rule_for_field(only)
        return self.__to_dict(ignore, only)

    def __to_dict(
            self,
            ignore: Set[str],
            only: Set[str],
            _prefix: str = '',
    ) -> dict:
        data = {}
        for k, v in self.__dict__.items():
            if _in_set(_prefix, k, ignore):
                continue
            if only and not _in_set(_prefix, k, only):
                continue
            data[k] = self.__get_value_from(
                v,
                ignore=ignore,
                only=only,
                _prefix=_new_prefix(_prefix, k),
            )
        return data

    def __get_value_from(
            self,
            v: Any,
            ignore: Set[str],
            only: Set[str],
            _prefix: str = '',
    ) -> Any:
        if isinstance(v, DataModel):
            return v.__to_dict(ignore=ignore, only=only, _prefix=_prefix)
        if isinstance(v, dict):
            data = {}
            for _k, _v in v.items():
                if _in_set(_prefix, _k, ignore):
                    continue
                if only and not _in_set(_prefix, _k, only):
                    continue
                data[_k] = self.__get_value_from(
                    _v,
                    ignore=ignore,
                    only=only,
                    _prefix=_new_prefix(_prefix, _k),
                )
            return data
        if isinstance(v, (list, set, tuple)):
            return [
                self.__get_value_from(
                    _v,
                    ignore=ignore,
                    only=only,
                    _prefix=_prefix,
                ) for _v in v
            ]
        if isinstance(v, Enum):
            return v.value
        return v

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(**obj)

    @classmethod
    def from_orm(
            cls,
            obj: BaseModelMixin,
            ignore: Union[str, List[str], Set[str]] = None,
            only: Union[str, List[str], Set[str]] = None,
            include: Union[str, List[str], Set[str]] = None,
    ):
        return cls.from_dict(
            obj.to_dict(
                ignore=ignore,
                only=only,
                include=include,
            )
        )


def _expand_rule_set(rule: Set[str]) -> dict:
    result = {}
    for r in rule:
        s = r.split('.')
        m = result
        for i in s[:-1]:
            if i not in m:
                m[i] = {}
            m = m[i]
        if s[-1] not in m:
            m[s[-1]] = None
    return result


def _make_ignore_rule(ignore: Union[str, List[str], Set[str]]) -> dict:
    return _expand_rule_set(make_ignore_rule_for_field(ignore))


def _make_only_rule(only: Union[str, List[str], Set[str]]) -> dict:
    return _expand_rule_set(make_only_rule_for_field(only))


def _in_set(prefix: str, key: str, s: set):
    return _new_prefix(prefix, key) in s


def _new_prefix(prefix: str, key: str):
    if not prefix:
        return key
    return prefix + '.' + key
