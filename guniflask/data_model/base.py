from typing import Union, List, Set

from pydantic import BaseModel

from guniflask.orm.base_model import BaseModelMixin
from guniflask.utils.rule import make_ignore_rule_for_field, make_only_rule_for_field


class DataModel(BaseModel):
    def to_dict(
            self,
            ignore: Union[str, List[str]] = None,
            only: Union[str, List[str]] = None,
    ) -> dict:
        kwargs = {}
        if ignore:
            kwargs['exclude'] = _make_ignore_rule(ignore)
        if only:
            kwargs['include'] = _make_only_rule(only)
        return self.dict()

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(**obj)

    @classmethod
    def from_orm(
            cls,
            obj: BaseModelMixin,
            ignore: Union[str, List[str]] = None,
            only: Union[str, List[str]] = None,
            include: Union[str, List[str]] = None,
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


def _make_ignore_rule(ignore: Union[str, List[str]]) -> dict:
    return _expand_rule_set(make_ignore_rule_for_field(ignore))


def _make_only_rule(only: Union[str, List[str]]) -> dict:
    return _expand_rule_set(make_only_rule_for_field(only))
