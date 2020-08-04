# coding=utf-8

from functools import update_wrapper
import inspect
from typing import List

from flask import Blueprint as FlaskBlueprint, request, current_app, g
from werkzeug.exceptions import BadRequest, InternalServerError
from werkzeug.routing import parse_rule

from guniflask.web.request_filter import RequestFilter, RequestFilterChain
from guniflask.beans.constructor_resolver import ConstructorResolver
from guniflask.web.filter_annotation import FilterChain
from guniflask.annotation.core import AnnotationUtils
from guniflask.beans.post_processor import BeanPostProcessorAdapter
from guniflask.web.bind_annotation import Blueprint, Route
from guniflask.utils.instantiation import instantiate_from_json, inspect_args
from guniflask.web.param_annotation import FieldInfo, RequestParam, PathVariable, \
    RequestParamInfo, PathVariableInfo, RequestBodyInfo, ContextParamInfo
from guniflask.web import param_annotation
from guniflask.beans.factory import BeanFactory, BeanFactoryAware
from guniflask.context.event_listener import ApplicationEventListener
from guniflask.context.event import ContextRefreshedEvent, ApplicationEvent
from guniflask.web.filter_annotation import MethodFilter
from guniflask.utils.instantiation import resolve_arg_type, ArgType

__all__ = ['BlueprintPostProcessor']


class BlueprintPostProcessor(BeanPostProcessorAdapter, ApplicationEventListener, BeanFactoryAware):
    def __init__(self):
        self.blueprints = []
        self._filter_chain_resolver: FilterChainResolver = None
        self._method_filter_resolver = MethodFilterResolver()

    def set_bean_factory(self, bean_factory: BeanFactory):
        self._filter_chain_resolver = FilterChainResolver(bean_factory)

    def on_application_event(self, application_event: ApplicationEvent):
        if isinstance(application_event, ContextRefreshedEvent):
            self._register_blueprints()

    def post_process_after_initialization(self, bean, bean_name: str):
        bean_type = bean.__class__
        annotation = AnnotationUtils.get_annotation(bean_type, Blueprint)
        if annotation is not None:
            options = annotation['options'] or {}
            b = FlaskBlueprint(bean_name, bean.__module__,
                               url_prefix=annotation['url_prefix'], **options)
            annotation['blueprint'] = b
            for m in dir(bean):
                method = getattr(bean, m)
                a = AnnotationUtils.get_annotation(method, Route)
                if a is not None:
                    rule_options = a['options'] or {}
                    b.add_url_rule(a['rule'],
                                   endpoint=method.__name__,
                                   view_func=self.wrap_view_func(a['rule'], method),
                                   **rule_options)
                self._method_filter_resolver.resolve(b, method)
            self.blueprints.append(b)
            self._filter_chain_resolver.add_blueprint(bean_type)
        return bean

    def wrap_view_func(self, rule: str, method):
        params, param_names = self._resolve_method_parameters(rule, method)

        def wrapper(**kwargs):
            method_kwargs = self._resolve_method_kwargs(kwargs, params, param_names)
            return method(**method_kwargs)

        return update_wrapper(wrapper, method)

    def _register_blueprints(self):
        self._filter_chain_resolver.build()

        for b in self.blueprints:
            current_app.register_blueprint(b)

    def _resolve_method_parameters(self, rule: str, method):
        """
        :param rule: path rule
        :param method: view function
        """
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

        args, type_hints = inspect_args(method)

        for arg, default in args.items():
            if default is inspect._empty:
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

    def _resolve_method_kwargs(self, kwargs: dict, params: dict, param_names: dict) -> dict:
        """
        :param kwargs: kwargs injected by Flask
        :param params: view function parameters
        :param param_names: names of the above parameters
        """
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
                    argc, etype = resolve_arg_type(p.dtype)
                    if argc is ArgType.LIST:
                        v = request.args.getlist(name)
                        if etype:
                            for i in range(len(v)):
                                v[i] = self._read_value(v[i], etype)
                    elif argc is ArgType.SINGLE:
                        v = request.args[name]
                        if p.dtype is not None:
                            v = self._read_value(v, p.dtype)
                    else:
                        raise ValueError('Unsupported request param type: {}'.format(p.dtype))

                    if v is not None:
                        result[k] = v
            elif isinstance(p, ContextParamInfo):
                name = p.name or k
                if name in g:
                    result[k] = g.get(name)
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

    def _read_value(self, v: str, dtype: type):
        if v is None:
            return
        if dtype == bool:
            try:
                return bool(int(v))
            except (ValueError, TypeError):
                if v in ("True", "true"):
                    return True
                if v in ("False", "false"):
                    return False
        else:
            try:
                return dtype(v)
            except (ValueError, TypeError):
                pass


class FilterChainResolver:
    def __init__(self, bean_factory: BeanFactory):
        self._constructor_resolver = ConstructorResolver(bean_factory)
        self._blueprints = []

    def add_blueprint(self, bean_type):
        self._blueprints.append(bean_type)

    def build(self):
        for bean_type in self._blueprints:
            filter_chain_annotation = AnnotationUtils.get_annotation(bean_type, FilterChain)
            if filter_chain_annotation is not None:
                request_filters = self._resolve_request_filters(filter_chain_annotation['values'])
                if request_filters:
                    chain = RequestFilterChain()
                    for f in request_filters:
                        chain.add_request_filter(f)

                    blueprint_annotation = AnnotationUtils.get_annotation(bean_type, Blueprint)
                    b = blueprint_annotation['blueprint']
                    b.before_request(chain.before_request)
                    b.after_request(chain.after_request)

    def _resolve_request_filters(self, values) -> List[RequestFilter]:
        if not hasattr(values, '__iter__'):
            values = [values]
        result = []
        for v in values:
            if isinstance(v, RequestFilter):
                result.append(v)
            else:
                f = self._constructor_resolver.instantiate(v)
                assert isinstance(f, RequestFilter), 'Required a request filter, ' \
                                                     'got: {}'.format(type(RequestFilter).__name__)
        return result


class MethodFilterResolver:

    def resolve(self, blueprint, method):
        a = AnnotationUtils.get_annotation(method, MethodFilter)
        if a is None:
            return
        for v in a['values']:
            name = v['name']
            args = v['args']
            if args is None:
                getattr(blueprint, name)(method)
            else:
                getattr(blueprint, name)(*args)(method)
