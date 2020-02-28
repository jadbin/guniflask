# coding=utf-8

import os
import signal
from threading import Thread, Event
import time
import logging
import sys
import errno
import inspect

from guniflask.app import create_app
from guniflask.utils.env import walk_modules

__all__ = ['BgProcess', 'BgProcessRunner']


class BgProcess:
    active = True
    log = logging.getLogger('gunicorn.error')

    def __init__(self):
        self.pid = None
        self.ppid = None

    def __str__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.pid)

    def run(self):
        raise NotImplemented

    def stop(self):
        pass

    def start(self):
        self._init_signals()

        def supervise():
            while True:
                if not self._is_parent_alive():
                    os.kill(self.pid, signal.SIGTERM)
                    return
                time.sleep(1)

        t = Thread(target=supervise, daemon=True)
        t.start()

        try:
            self.run()
        except SystemExit:
            raise
        except Exception:
            self.log.warning('Error during %s run', self, exc_info=True)

    def _is_parent_alive(self):
        if self.ppid != os.getppid():
            self.log.info('Parent changed, shutting down: %s', self)
            return False
        return True

    def _init_signals(self):
        def handle_shutdown(signum, frame):
            self._shutdown()

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGQUIT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

    def _shutdown(self):
        try:
            self.stop()
        except Exception:
            self.log.warning('Error during %s exit', self, exc_info=True)
        sys.exit(0)


class BgProcessRunner:
    log = logging.getLogger('gunicorn.error')

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.bg_processes = set()
        self.pid = None
        self.ppid = None

    def __str__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.pid)

    def start(self):
        self.log.info('Starting: %s', self.__class__.__name__)

        self.ppid = os.getpid()

        pid = os.fork()
        if pid != 0:
            self.pid = pid
            return pid

        self.pid = os.getpid()
        self._init_signals()

        def supervise():
            while True:
                if not self._is_parent_alive():
                    os.kill(self.pid, signal.SIGTERM)
                    return
                time.sleep(1)

        t = Thread(target=supervise, daemon=True)
        t.start()

        self.start_bg_processes()

        event = Event()
        try:
            event.wait()
        finally:
            os._exit(0)

    def stop(self):
        try:
            os.kill(self.pid, signal.SIGTERM)
        except OSError as e:
            if e.errno == errno.ESRCH:
                return
            raise

    def _init_signals(self):
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGQUIT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        self._shutdown()

    def _is_parent_alive(self):
        if self.ppid != os.getppid():
            self.log.info('Parent changed, shutting down: %s', self)
            return False
        return True

    def _shutdown(self):
        self.log.info('Shutting down: %s', self.__class__.__name__)
        self.kill_bg_processes(signal.SIGTERM)
        sys.exit(0)

    def start_bg_processes(self):

        def iter_bg_processes():
            for module in walk_modules(self.name):
                for obj in vars(module).values():
                    if inspect.isclass(obj) and obj.__module__ == module.__name__ and issubclass(obj, BgProcess):
                        if obj.active:
                            yield obj

        for bg_cls in iter_bg_processes():
            self.start_bg_process(bg_cls)

    def start_bg_process(self, bg_cls):
        pid = os.fork()
        if pid != 0:
            self.bg_processes.add(pid)
            return pid

        app = create_app(self.name)
        with app.app_context():
            bg = bg_cls()
            bg.pid = os.getpid()
            bg.ppid = self.pid
            self.log.info('Booting %s with pid: %s', bg_cls.__name__, bg.pid)
            try:
                bg.start()
            finally:
                self.log.info('%s exiting (pid: %s)', bg_cls.__name__, bg.pid)
                os._exit(0)

    def kill_bg_processes(self, sig):
        pid_list = list(self.bg_processes)
        for pid in pid_list:
            self.kill_bg_process(pid, sig)
            self.bg_processes.remove(pid)

    def kill_bg_process(self, pid, sig):
        try:
            os.kill(pid, sig)
        except OSError as e:
            if e.errno == errno.ESRCH:
                return
            raise
