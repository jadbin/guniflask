import os
import uuid
from os.path import isfile, join

from guniflask.utils.network import get_local_ip_address


def load_config(fname, **kwargs) -> dict:
    if fname is None or not isfile(fname):
        raise FileNotFoundError(f"Cannot find configuration file '{fname}'")
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


def load_profile_config(conf_dir, name, profiles=None, **kwargs) -> dict:
    base_file = join(conf_dir, name + '.py')
    if isfile(base_file):
        pc = load_config(base_file, **kwargs)
    else:
        pc = {}
    if profiles:
        profiles = profiles.split(',')
        for profile in reversed(profiles):
            if profile:
                pc_file = join(conf_dir, name + '_' + profile + '.py')
                if isfile(pc_file):
                    c = load_config(pc_file, **kwargs)
                    _update_config(pc, c)
        pc['active_profiles'] = list(profiles)
    return pc


def _update_config(old: dict, new: dict):
    for k, v in new.items():
        if k not in old:
            old[k] = v
        else:
            if isinstance(v, dict) and isinstance(old[k], dict):
                _update_config(old[k], v)
            else:
                old[k] = v


def load_app_settings(app_name) -> dict:
    c = {}
    conf_dir = os.environ.get('GUNIFLASK_CONF_DIR')
    active_profiles = os.environ.get('GUNIFLASK_ACTIVE_PROFILES')
    kwargs = get_settings_from_env()
    kwargs['app_name'] = app_name
    if conf_dir:
        c = load_profile_config(conf_dir, app_name, profiles=active_profiles, **kwargs)
    if 'app_id' not in c:
        c['app_id'] = uuid.uuid4().hex
    if 'ip_address' not in c:
        c['ip_address'] = get_local_ip_address()

    s = {}
    for name in c:
        if not name.startswith('_'):
            s[name] = c[name]
    return s


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
    return kwargs
