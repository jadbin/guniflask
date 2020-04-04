# coding=utf-8

import os


def daemonize():
    if os.fork():
        os._exit(0)
    os.setsid()
    if os.fork():
        os._exit(0)
    os.umask(0o22)
    os.closerange(0, 3)
    fd_null = os.open(os.devnull, os.O_RDWR)
    if fd_null != 0:
        os.dup2(fd_null, 0)
    os.dup2(fd_null, 1)
    os.dup2(fd_null, 2)


def pid_exists(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def get_master_pid():
    return os.getppid()
