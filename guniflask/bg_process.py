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
from guniflask.utils.config import load_object


class BgProcess:
    def __init__(self, app):
        self.app = app
        self.settings = app.extensions['settings']
        self.configure_logging()
        self.logger = logging.getLogger(self.app.name + '.bg')

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
        try:
            with self.app.app_context():
                self.run()
        except Exception:
            self.logger.error('error occurred in %s', self.__class__.__name__, exc_info=True)


class BgProcessRunner:
    def __init__(self, name=None, bg_cls=None, on_starting=None):
        self.name = name
        self.bg_cls = bg_cls
        self.on_starting = on_starting
        self.debug = os.environ.get('GUNIFLASK_DEBUG')
        self.bg = None

    def start(self, server):
        if self.on_starting is not None:
            self.on_starting(server)
        pid = os.getpid()
        p = Process(target=self._start_bg_process, args=(pid,))
        p.start()
        p.join()

    def _start_bg_process(self, pid):
        daemonize()
        self._bg_init_signals()
        t = Thread(target=self._bg_supervisor, args=(pid,))
        t.start()
        app = create_bg_process_app(self.name)
        bg_cls = self.bg_cls
        if isinstance(bg_cls, str):
            bg_cls = load_object(bg_cls)
        self.bg = bg_cls(app)
        self.bg.start()

    def _bg_init_signals(self):
        def _exit(signum, frame):
            self._bg_exit()

        signal.signal(signal.SIGINT, _exit)
        signal.signal(signal.SIGTERM, _exit)

    def _bg_supervisor(self, pid):
        while True:
            if not existsp(pid):
                self._bg_exit()
            time.sleep(1)

    def _bg_exit(self):
        if self.bg:
            self.bg.logger.info('%s exiting (pid: %s)', self.bg.__class__.__name__, os.getpid())
        os._exit(0)


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
