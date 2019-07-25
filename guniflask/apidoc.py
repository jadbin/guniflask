# coding=utf-8

from os.path import join

from flask import current_app, Blueprint, render_template, _app_ctx_stack
from werkzeug.local import LocalProxy

from guniflask.config import settings
from guniflask.utils.template import template_folder
from guniflask.utils.config import walk_modules

static_folder = join(template_folder, 'static')

apidoc = Blueprint('apidoc', __name__, url_prefix='/_apidoc',
                   template_folder=join(template_folder, 'apidoc'),
                   static_folder=static_folder,
                   static_url_path='/static')

api_doc = LocalProxy(lambda: current_app.extensions['apidoc'])


@apidoc.route('/', methods=['GET'])
def get_api_modules():
    api_module_keys = _get_api_module_keys()
    return render_template('api_modules.html', api_module_keys=api_module_keys, api_modules=api_doc.api_modules,
                           project_name=settings['project_name'])


def _get_api_module_keys():
    api_modules = api_doc.api_modules
    keys = [i for i in api_modules.keys()]
    keys.sort(key=lambda x: api_modules[x]['url_prefix'])
    return keys


@apidoc.route('/<module>', methods=['GET'])
def get_api_list(module):
    api_list = _get_api_list(module)
    return render_template('api_list.html', api_list=api_list, module=module, project_name=settings['project_name'])


def _get_api_list(module):
    api_set = api_doc.api_set
    api_list = []
    for k, v in api_set.items():
        if k.startswith(module + '.'):
            api_list.append(v)
    api_list.sort(key=lambda x: x['path'])
    return api_list


class ApiDoc:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.register_blueprint(apidoc)
        app.extensions['apidoc'] = self

    @property
    def api_modules(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'api_modules'):
                self.make_api_docs()
            return ctx.api_modules

    @property
    def api_set(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'api_set'):
                self.make_api_docs()
            return ctx.api_set

    def make_api_docs(self):
        app = current_app
        ctx = _app_ctx_stack.top
        api_modules = {}
        api = {}

        for module in walk_modules(app.name):
            for obj in vars(module).values():
                if isinstance(obj, Blueprint):
                    doc = module.__doc__
                    if doc:
                        doc = doc.rstrip()
                    api_modules[obj.name] = dict(name=obj.name, url_prefix=obj.url_prefix, doc=doc)
        rules = {}
        for i in app.url_map.iter_rules():
            rules[i.endpoint] = i
        for e, r in rules.items():
            f = app.view_functions[e]
            name = ' '.join([i.title() for i in f.__name__.split('_')])
            methods = [i for i in r.methods if i not in ['HEAD', 'OPTIONS']]
            methods.sort()
            methods = ', '.join(methods)
            doc = f.__doc__
            if doc:
                doc = doc.rstrip()
            api[e] = dict(name=name, endpoint=e, path=r.rule, methods=methods, doc=doc)

        ctx.api_modules = api_modules
        ctx.api_set = api
