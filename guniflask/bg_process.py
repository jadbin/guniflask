# coding=utf-8

import os
from multiprocessing import Process
import signal
from threading import Thread
import time

from guniflask.app import create_bg_process_app


class BgProcess:
    def __init__(self, app):
        self.app = app
        self.settings = app.extensions['settings']

    def run(self):
        raise NotImplemented

    def start(self):
        with self.app.app_context():
            self.run()


def start_bg_process(server, name=None, bg_cls=None, on_starting=None):
    def start(pid):
        daemonize()
        init_signals()
        t = Thread(target=supervisor, args=(pid,))
        t.start()
        app = create_bg_process_app(name)
        bg = bg_cls(app)
        bg.start()

    def init_signals():
        def _exit(signum, frame):
            os._exit(0)

        signal.signal(signal.SIGINT, _exit)
        signal.signal(signal.SIGTERM, _exit)

    def supervisor(pid):
        while True:
            if not existsp(pid):
                os._exit(0)
            time.sleep(3)

    if on_starting is not None:
        on_starting(server)
    assert issubclass(bg_cls, BgProcess)
    pid = os.getpid()
    p = Process(target=start, args=(pid,))
    p.start()
    p.join()


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


def existsp(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True
