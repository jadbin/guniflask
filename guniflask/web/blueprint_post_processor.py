# coding=utf-8

from functools import update_wrapper
import inspect
from typing import List

from flask import Flask, Blueprint as FlaskBlueprint, request
from werkzeug.exceptions import BadRequest, InternalServerError
from werkzeug.routing import parse_rule

from guniflask.annotation.core import AnnotationUtils
from guniflask.beans.post_processor import BeanPostProcessorAdapter
from guniflask.web.bind_annotation import Blueprint, Route
from guniflask.utils.factory import instantiate_from_json
from guniflask.web.param_annotation import FieldInfo, RequestParam, PathVariable, \
    RequestParamInfo, PathVariableInfo, RequestBodyInfo
from guniflask.web import param_annotation
from guniflask.beans.factory import BeanFactory
from guniflask.web.filter_chain_resolver import FilterChainResolver
from guniflask.web.filter_annotation import FilterChain

__all__ = ['BlueprintPostProcessor']


class BlueprintPostProcessor(BeanPostProcessorAdapter):
    def __init__(self, app: Flask, bean_factory: BeanFactory):
        self.app = app
        self._filter_chain_resolver = FilterChainResolver(bean_factory)

    def post_process_after_initialization(self, bean, bean_name: str):
        bean_type = bean.__class__
        annotation = AnnotationUtils.get_annotation(bean_type, Blueprint)
        if annotation is not None:
            options = annotation['options'] or {}
            b = FlaskBlueprint(bean_name, bean.__module__,
                               url_prefix=annotation['url_prefix'], **options)
            for m in dir(bean):
                method = getattr(bean, m)
                a = AnnotationUtils.get_annotation(method, Route)
                if a is not None:
                    rule_options = a['options'] or {}
                    b.add_url_rule(a['rule'],
                                   endpoint=method.__name__,
                                   view_func=self.wrap_view_func(a['rule'], method),
                                   **rule_options)

            filter_chain_annotation = AnnotationUtils.get_annotation(bean_type, FilterChain)
            if filter_chain_annotation is not None:
                self._filter_chain_resolver.register_request_filters(b, filter_chain_annotation['values'])
            
            self.app.register_blueprint(b)
        return bean

    def wrap_view_func(self, rule: str, method):
        params, param_names = self._resolve_method_parameters(rule, method)

        def wrapper(**kwargs):
            method_kwargs = self._resolve_method_kwargs(kwargs, params, param_names)
            return method(**method_kwargs)

        return update_wrapper(wrapper, method)

    def _resolve_method_parameters(self, rule: str, method):
        params = {}
        param_names = {}

        # resolve path variable in route
        path_variable_type = {}
        for converter, _, name in parse_rule(rule):
            if converter is None:
                continue
            if converter == 'int':
                path_variable_type[name] = int
            elif converter == 'float':
                path_variable_type[name] = float
            else:
                path_variable_type[name] = str

        spec = inspect.getfullargspec(method)
        spec_args = spec.args or []
        if len(spec.args) > 0 and spec_args[0] in ('self', 'cls'):
            spec_args = spec_args[1:]
        spec_defaults = list(spec.defaults) if spec.defaults else []
        NO_VALUE = object()
        while len(spec_defaults) < len(spec_args):
            spec_defaults.insert(0, NO_VALUE)
        spec_kwargs = spec.kwonlydefaults or {}
        type_hints = spec.annotations

        for arg, default in self._get_arg_with_default(spec_args, spec_defaults, spec_kwargs):
            if default is NO_VALUE:
                required = True
                default = None
            else:
                required = False
            if inspect.isfunction(default) and getattr(param_annotation, default.__name__, None) is default:
                default = default()
            if not isinstance(default, FieldInfo):
                if arg in path_variable_type:
                    annotation = PathVariable(dtype=None if arg in type_hints else path_variable_type[arg])
                else:
                    annotation = RequestParam()
                annotation.default = default
                default = annotation
            if arg in type_hints and default.dtype is None:
                default.dtype = type_hints[arg]
            if default.required is None:
                default.required = required
            params[arg] = default
            if default.name is not None:
                param_names[default.name] = arg

        return params, param_names

    def _get_arg_with_default(self, args: list, defaults: list, kwargs: dict):
        for i in range(0, len(args)):
            yield args[i], defaults[i]
        for i in kwargs:
            yield i, kwargs[i]

    def _resolve_method_kwargs(self, kwargs: dict, params: dict, param_names: dict) -> dict:
        result = {}
        for k, v in kwargs.items():
            if k in param_names:
                k = param_names[k]
            if k not in params:
                raise InternalServerError('Unhandled parameter: {}={}'.format(k, v))
            if params[k].dtype is not None:
                try:
                    v = params[k].dtype(v)
                except ValueError:
                    pass
            result[k] = v
        for k, p in params.items():
            if k in result:
                continue
            name = p.name or k
            if isinstance(p, PathVariableInfo):
                raise InternalServerError('No such path variable: {}'.format(name))

            if isinstance(p, RequestParamInfo):
                if name in request.args:
                    if p.dtype and issubclass(p.dtype, List):
                        v = request.args.getlist(name)
                        if hasattr(p.dtype, '__args__'):
                            args = getattr(p.dtype, '__args__')
                            if args is not None and len(args) == 1:
                                element_type = args[0]
                                if inspect.isclass(element_type):
                                    for i in range(len(v)):
                                        try:
                                            v[i] = element_type(v[i])
                                        except ValueError:
                                            pass
                    else:
                        v = request.args[name]
                        if p.dtype is not None:
                            try:
                                v = p.dtype(v)
                            except ValueError:
                                pass
                    if v is not None:
                        result[k] = v
            elif isinstance(p, RequestBodyInfo):
                # FIXME: handle files, multi-parts, etc.
                data = request.json
                v = instantiate_from_json(data, dtype=p.dtype)
                if v is not None:
                    result[k] = v

            if k not in result:
                if p.required:
                    if isinstance(p, RequestBodyInfo):
                        raise BadRequest('Request body not given or in wrong format')
                    else:
                        raise BadRequest('Parameter not given: {}'.format(name))
                result[k] = p.default
        return result
