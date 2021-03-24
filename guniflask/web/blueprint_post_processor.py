import datetime as dt
import inspect
import logging
from functools import update_wrapper
from typing import Optional

from flask import Blueprint as FlaskBlueprint, request, current_app
from werkzeug.exceptions import BadRequest, InternalServerError
from werkzeug.routing import parse_rule

from guniflask.annotation import AnnotationUtils
from guniflask.beans.post_processor import BeanPostProcessor
from guniflask.context.event import ContextRefreshedEvent, ApplicationEvent
from guniflask.context.event_listener import ApplicationEventListener
from guniflask.data_model.typing import parse_json, inspect_args, analyze_arg_type
from guniflask.utils.datatime import convert_to_datetime
from guniflask.web import request_annotation
from guniflask.web.bind_annotation import Blueprint, Route
from guniflask.web.filter_annotation import MethodDefFilter
from guniflask.web.request_annotation import FieldInfo, RequestParam, PathVariable, RequestParamInfo, PathVariableInfo, \
    RequestBodyInfo, FilePartInfo, FormValueInfo, RequestHeaderInfo, CookieValueInfo, RequestBody

log = logging.getLogger(__name__)


class BlueprintPostProcessor(BeanPostProcessor, ApplicationEventListener):
    def __init__(self):
        self.blueprints = []

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
            for m in dir(bean_type):
                func = getattr(bean_type, m)
                if inspect.isfunction(func):
                    method = getattr(bean, m)
                    try:
                        self._resolve_route(b, method)
                        self._resolve_method_def_filter(b, method)
                    except Exception:
                        log.error(
                            "Failed to resolve the route function '%s' in blueprint '%s'",
                            m,
                            bean_type.__name__,
                        )
                        raise
            self.blueprints.append(b)
        return bean

    def _resolve_route(self, blueprint: FlaskBlueprint, method):
        a = AnnotationUtils.get_annotation(method, Route)
        if a is not None:
            rule_options = a['options'] or {}
            blueprint.add_url_rule(
                a['rule'],
                endpoint=method.__name__,
                view_func=self._wrap_view_func(a['rule'], method),
                **rule_options
            )

    def _wrap_view_func(self, rule: str, method):
        params, param_names = self._resolve_method_parameters(rule, method)

        def wrapper(**kwargs):
            method_kwargs = self._resolve_method_kwargs(kwargs, params, param_names)
            return method(**method_kwargs)

        return update_wrapper(wrapper, method)

    def _resolve_method_def_filter(self, blueprint, method):
        a = AnnotationUtils.get_annotation(method, MethodDefFilter)
        if a is None:
            return
        for v in a['values']:
            name = v['name']
            args = v['args']
            if args is None:
                getattr(blueprint, name)(method)
            else:
                getattr(blueprint, name)(*args)(method)

    def _register_blueprints(self):
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
            if inspect.isfunction(default) and getattr(request_annotation, default.__name__, None) is default:
                default = default()
            if not isinstance(default, FieldInfo):
                if arg in path_variable_type:
                    annotation = PathVariable(dtype=None if arg in type_hints else path_variable_type[arg])
                else:
                    if arg in type_hints:
                        arg_type = type_hints[arg]
                        arg_ = analyze_arg_type(arg_type)
                        if arg_.is_dict():
                            annotation = RequestBody()
                        else:
                            annotation = RequestParam()
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
                raise InternalServerError(f'Unhandled parameter: {k}={v}')
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
                raise InternalServerError(f'No such path variable: {name}')

            if isinstance(p, RequestParamInfo):
                if name in request.args:
                    arg_ = analyze_arg_type(p.dtype)
                    if arg_.is_list():
                        v = request.args.getlist(name)
                        if arg_.outer_type:
                            for i in range(len(v)):
                                v[i] = self._read_value(v[i], arg_.outer_type)
                    elif arg_.is_singleton():
                        v = request.args.get(name)
                        if p.dtype is not None:
                            v = self._read_value(v, p.dtype)
                    else:
                        raise BadRequest(f'Unsupported type of parameter "{name}": {p.dtype}')
                    if v is not None:
                        result[k] = v
            elif isinstance(p, RequestBodyInfo):
                data = request.json
                v = parse_json(data, dtype=p.dtype)
                if v is not None:
                    result[k] = v
            elif isinstance(p, FilePartInfo):
                file = request.files.get(name)
                if file is not None:
                    if p.dtype == bytes:
                        result[k] = file.read()
                    else:
                        result[k] = file
            elif isinstance(p, FormValueInfo):
                arg_ = analyze_arg_type(p.dtype)
                if arg_.is_list():
                    v = request.form.getlist(name)
                    if arg_.outer_type:
                        for i in range(len(v)):
                            v[i] = self._read_value(v[i], arg_.outer_type)
                elif arg_.is_singleton():
                    v = request.form.get(name)
                    if p.dtype is not None:
                        v = self._read_value(v, p.dtype)
                else:
                    raise BadRequest(f'Unsupported type of parameter "{name}": {p.dtype}')
                if v is not None:
                    result[k] = v
            elif isinstance(p, RequestHeaderInfo):
                arg_ = analyze_arg_type(p.dtype)
                if arg_.is_list():
                    v = request.headers.getlist(name)
                    if arg_.outer_type:
                        for i in range(len(v)):
                            v[i] = self._read_value(v[i], arg_.outer_type)
                elif arg_.is_singleton():
                    v = request.headers.get(name)
                    if p.dtype is not None:
                        v = self._read_value(v, p.dtype)
                else:
                    raise BadRequest(f'Unsupported type of header "{name}": {p.dtype}')
                if v is not None:
                    result[k] = v
                v = self._read_value(request.headers.get(name), p.dtype)
                if v is not None:
                    result[k] = v
            elif isinstance(p, CookieValueInfo):
                v = request.cookies.get(name)
                if v is not None:
                    if p.dtype is not None:
                        v = self._read_value(v, p.dtype)
                    result[k] = v

            if k not in result:
                if p.required:
                    if isinstance(p, RequestBodyInfo):
                        raise BadRequest('Request body not given or in wrong format')
                    else:
                        raise BadRequest(f'Parameter not given: {name}')
                result[k] = p.default
        return result

    def _read_value(self, v: Optional[str], dtype: type):
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
        elif dtype == dt.datetime:
            return convert_to_datetime(v)
        else:
            try:
                return dtype(v)
            except (ValueError, TypeError):
                raise BadRequest(f'The expected type is "{dtype.__name__}": {v}')
