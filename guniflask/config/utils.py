# coding=utf-8


__all__ = ['map_dict_config']


def map_dict_config(source: dict, target):
    for k in source:
        if hasattr(target, k):
            v = source[k]
            if isinstance(v, dict):
                map_dict_config(v, getattr(target, k))
            else:
                setattr(target, k, v)
