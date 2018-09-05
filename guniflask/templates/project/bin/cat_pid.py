# coding=utf-8

import sys
from os.path import isfile


def _get_config(fname):
    if fname is None or not isfile(fname):
        sys.exit(1)

    code = compile(open(fname, 'rb').read(), fname, 'exec')
    cfg = {
        "__builtins__": __builtins__,
        "__name__": "__config__",
        "__file__": fname,
        "__doc__": None,
        "__package__": None
    }
    exec(code, cfg, cfg)

    return cfg


def cat_pid(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) < 2:
        sys.exit(1)
    del argv[0]
    pidfile = _get_config(argv[0])['pidfile']
    if not isfile(pidfile):
        sys.exit(1)
    with open(pidfile, 'r') as f:
        line = f.readline()
        if line:
            print(line.strip())


if __name__ == '__main__':
    cat_pid()
