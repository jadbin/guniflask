from typing import Union, List, Set


def _make_rule_set(rule: Union[str, List[str], Set[str]]):
    if isinstance(rule, str):
        rule = [i.strip() for i in rule.split(',')]
    return set(rule or [])


def make_ignore_rule_for_field(field: Union[str, List[str], Set[str]]):
    if isinstance(field, set):
        return field
    return _make_rule_set(field)


def make_include_rule_for_field(field: Union[str, List[str], Set[str]]) -> set:
    if isinstance(field, set):
        return field
    return _make_rule_set(field)


def make_only_rule_for_field(field: Union[str, List[str], Set[str]]) -> set:
    if isinstance(field, set):
        return field
    s = _make_rule_set(field)
    for k in list(s):
        if '.' in k:
            t = k.split('.')
            for i in range(1, len(t)):
                s.add('.'.join(t[:i]))
    return s
