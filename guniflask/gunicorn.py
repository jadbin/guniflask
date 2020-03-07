# coding=utf-8

import os
from os.path import join, dirname, exists
import multiprocessing

from gunicorn.config import KNOWN_SETTINGS
from gunicorn.app.base import Application

from guniflask.config.app_config import load_profile_config
from guniflask.utils.env import walk_files
from guniflask.app import create_app
from guniflask.cli.env import get_project_name_from_env

__all__ = ['GunicornApplication']


class GunicornApplication(Application):

    def __init__(self):
        self.options = self._make_options()
        super().__init__()

    def set_option(self, key, value):
        if key in self.cfg.settings:
            self.cfg.set(key, value)

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return create_app(get_project_name_from_env())

    def _make_options(self):
        pid_dir = os.environ['GUNIFLASK_PID_DIR']
        log_dir = os.environ['GUNIFLASK_LOG_DIR']
        id_string = os.environ['GUNIFLASK_ID_STRING']
        project_name = get_project_name_from_env()
        options = {
            'daemon': True,
            'workers': multiprocessing.cpu_count(),
            'worker_class': 'gevent',
            'pidfile': join(pid_dir, '{}-{}.pid'.format(project_name, id_string)),
            'accesslog': join(log_dir, '{}-{}.access.log'.format(project_name, id_string)),
            'errorlog': join(log_dir, '{}-{}.error.log'.format(project_name, id_string))
        }
        options.update(self._make_profile_options(os.environ.get('GUNIFLASK_ACTIVE_PROFILES')))
        # if debug
        if os.environ.get('GUNIFLASK_DEBUG'):
            options.update(self._make_debug_options())
        self._makedirs(options)
        # hook wrapper
        self._set_hook_wrapper(options)
        return options

    def _set_hook_wrapper(self, options):
        HookWrapper.from_config(options)

    def _make_profile_options(self, active_profiles):
        conf_dir = os.environ['GUNIFLASK_CONF_DIR']
        gc = load_profile_config(conf_dir, 'gunicorn', profiles=active_profiles)
        settings = {}
        snames = set([i.name for i in KNOWN_SETTINGS])
        for name in gc:
            if name in snames:
                settings[name] = gc[name]
        return settings

    @staticmethod
    def _make_debug_options():
        conf_dir = os.environ['GUNIFLASK_CONF_DIR']
        return {
            'accesslog': '-',
            'errorlog': '-',
            'loglevel': 'debug',
            'disable_redirect_access_to_syslog': True,
            'reload': True,
            'reload_extra_files': walk_files(conf_dir),
            'workers': 1,
            'daemon': False
        }

    @staticmethod
    def _makedirs(opts):
        for c in ['pidfile', 'accesslog', 'errorlog']:
            p = opts.get(c)
            if p:
                d = dirname(p)
                if d and not exists(d):
                    os.makedirs(d)


class HookWrapper:
    HOOKS = ['on_starting', 'on_reload', 'on_exit']

    def __init__(self, config, on_starting=None, on_reload=None, on_exit=None):
        self.config = config
        self._on_starting = on_starting
        self._on_reload = on_reload
        self._on_exit = on_exit

    @classmethod
    def from_config(cls, config):
        kw = {}
        for h in cls.HOOKS:
            kw[h] = config.get(h)
        wrapper = cls(config, **kw)
        for h in cls.HOOKS:
            config[h] = getattr(wrapper, h)
        return wrapper

    def on_starting(self, server):
        if self._on_starting is not None:
            self._on_starting(server)

    def on_reload(self, server):
        if self._on_reload is not None:
            self._on_reload(server)

    def on_exit(self, server):
        if self._on_exit is not None:
            self._on_exit(server)
