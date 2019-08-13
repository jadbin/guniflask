# coding=utf-8

import os
from multiprocessing import Process
import signal
from threading import Thread
import time
from os.path import join
from logging.config import dictConfig
import logging

from gunicorn.glogging import Logger

from guniflask.app import create_bg_process_app


class BgProcess:
    def __init__(self, app):
        self.app = app
        self.settings = app.extensions['settings']
        self.configure_logging()

    def configure_logging(self):
        if 'bg_log_config' in self.settings:
            dictConfig(self.settings['bg_log_config'])
        else:
            logger = logging.getLogger(self.app.name)
            debug = os.environ.get('GUNIFLASK_DEBUG')
            if debug:
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)
            log_dir = os.environ['GUNIFLASK_LOG_DIR']
            id_string = os.environ['GUNIFLASK_ID_STRING']
            project_name = os.environ.get('GUNIFLASK_PROJECT_NAME')
            log_file = join(log_dir, 'bg-{}-{}.log'.format(project_name, id_string))
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(Logger.error_fmt, Logger.datefmt)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

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
