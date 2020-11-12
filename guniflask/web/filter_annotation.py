from guniflask.annotation import Annotation, AnnotationUtils


class MethodDefFilter(Annotation):
    def add_filter(self, name, args=None):
        if 'values' not in self:
            self['values'] = []
        self['values'].append({'name': name, 'args': args})

    def get_filters(self):
        if 'values' not in self:
            return []
        return self['values']


def _add_method_def_filter_annotation(func, name, args=None):
    a = AnnotationUtils.get_annotation(func, MethodDefFilter)
    if a is None:
        a = MethodDefFilter()
        AnnotationUtils.add_annotation(func, a)
    a.add_filter(name, args=args)


def before_request(func):
    _add_method_def_filter_annotation(func, 'before_request')
    return func


def after_request(func):
    _add_method_def_filter_annotation(func, 'after_request')
    return func


def app_before_request(func):
    _add_method_def_filter_annotation(func, 'app_before_request')
    return func


def app_after_request(func):
    _add_method_def_filter_annotation(func, 'app_after_request')
    return func


def error_handler(code_or_exception):
    def wrap_func(func):
        _add_method_def_filter_annotation(func, 'errorhandler', args=[code_or_exception])
        return func

    return wrap_func


def app_error_handler(code_or_exception):
    def wrap_func(func):
        _add_method_def_filter_annotation(func, 'app_errorhandler', args=[code_or_exception])
        return func

    return wrap_func
