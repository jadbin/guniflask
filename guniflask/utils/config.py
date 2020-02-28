# coding=utf-8

from os.path import isfile, join


def load_config(fname, **kwargs):
    if fname is None or not isfile(fname):
        raise FileNotFoundError("Cannot find configuration file '{}'".format(fname))
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


def load_profile_config(conf_dir, name, profiles=None, **kwargs):
    pc = load_config(join(conf_dir, name + '.py'), **kwargs)
    if profiles:
        profiles = profiles.split(',')
        profiles.reverse()
        for profile in profiles:
            if profile:
                pc_file = join(conf_dir, name + '_' + profile + '.py')
                if isfile(pc_file):
                    c = load_config(pc_file, **kwargs)
                    pc.update(c)
    return pc
