import json
import os
import uuid
from os.path import isfile, join

import yaml

from guniflask.utils.network import get_local_ip_address


def _load_config(fname, **kwargs) -> dict:
    if fname is None or not isfile(fname):
        raise FileNotFoundError(f"Cannot find configuration file '{fname}'")

    s = {}
    if fname.endswith('.py'):
        s = _load_py_config(fname, **kwargs)
    if fname.endswith('.yaml') or fname.endswith('.yml'):
        s = _load_yaml_config(fname, **kwargs)
    if fname.endswith('.json'):
        s = _load_json_config(fname, **kwargs)

    _s = {}
    for name in s:
        if not name.startswith('_'):
            _s[name] = s[name]
    return _s


def _load_py_config(fname: str, **kwargs) -> dict:
    code = compile(open(fname, 'rb').read(), fname, 'exec')
    cfg = {
        "__builtins__": __builtins__,
        "__name__": "__config__",
        "__file__": fname,
        "__doc__": None,
        "__package__": None
    }
    cfg.update(kwargs)
    exec(code, cfg, cfg)
    return cfg


def _load_yaml_config(fname: str, **kwargs) -> dict:
    s = dict(**kwargs)
    with open(fname, 'rb') as f:
        s.update(yaml.safe_load(f))
    return s


def _load_json_config(fname: str, **kwargs) -> dict:
    s = dict(**kwargs)
    with open(fname, 'r') as f:
        s.update(json.load(f))
    return s


def load_profile_config(conf_dir: str, name: str, **kwargs) -> dict:
    _config_ext = ['.py', '.yaml', '.yml', '.json']

    pc = {}
    base_files = [join(conf_dir, name + ext) for ext in _config_ext]
    for file in base_files:
        try:
            pc = _load_config(file, **kwargs)
        except FileNotFoundError:
            pass
        else:
            break

    profiles = kwargs.get('active_profiles')
    if profiles:
        profiles = profiles.split(',')
        for profile in reversed(profiles):
            if profile:
                files = [join(conf_dir, name + '_' + profile + ext) for ext in _config_ext]
                for file in files:
                    try:
                        c = _load_config(file, **kwargs)
                    except FileNotFoundError:
                        pass
                    else:
                        _merge_config(pc, c)
                        break

    return pc


def _merge_config(old: dict, new: dict):
    for k, v in new.items():
        if k not in old:
            old[k] = v
        else:
            if isinstance(v, dict) and isinstance(old[k], dict):
                _merge_config(old[k], v)
            else:
                old[k] = v


def load_app_settings(app_name) -> dict:
    c = {}
    conf_dir = os.environ.get('GUNIFLASK_CONF_DIR')
    kwargs = get_settings_from_env()
    kwargs['app_name'] = app_name
    if conf_dir:
        c = load_profile_config(conf_dir, app_name, **kwargs)
    if 'ip_address' not in c:
        c['ip_address'] = get_local_ip_address()
    return c


def get_settings_from_env() -> dict:
    kwargs = {
        'home': os.environ.get('GUNIFLASK_HOME'),
    }
    if os.environ.get('GUNIFLASK_DEBUG'):
        kwargs['debug'] = True
    else:
        kwargs['debug'] = False
    kwargs['host'] = os.environ.get('GUNIFLASK_HOST')
    port = os.environ.get('GUNIFLASK_PORT')
    if port:
        port = int(port)
    kwargs['port'] = port
    active_profiles = os.environ.get('GUNIFLASK_ACTIVE_PROFILES')
    kwargs['active_profiles'] = active_profiles
    return kwargs
