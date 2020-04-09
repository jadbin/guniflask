# coding=utf-8

from guniflask.orm.model_utils import model_to_dict, dict_to_model, update_model_by_dict, result_to_dict

__all__ = ['wrap_sqlalchemy_model']


def wrap_sqlalchemy_model(model_cls):
    if not hasattr(model_cls, 'to_dict'):
        model_cls.to_dict = lambda self, **kwargs: model_to_dict(self, **kwargs)
    if not hasattr(model_cls, 'from_dict'):
        model_cls.from_dict = classmethod(lambda cls, dict_obj, **kwargs: dict_to_model(dict_obj, cls, **kwargs))
    if not hasattr(model_cls, 'update_by_dict'):
        model_cls.update_by_dict = lambda self, dict_obj, **kwargs: update_model_by_dict(self, dict_obj, **kwargs)
    if not hasattr(model_cls, 'result_to_dict'):
        model_cls.result_to_dict = classmethod(lambda cls, result, **kwargs: result_to_dict(result, cls, **kwargs))
    return model_cls
