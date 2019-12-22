# coding=utf-8

import sys
import os
from os.path import isfile, join, dirname, exists, isdir
import argparse
import signal
import time
import multiprocessing
import json

from sqlalchemy.schema import MetaData

from gunicorn.config import KNOWN_SETTINGS
from gunicorn.app.base import Application

from guniflask.utils.config import walk_modules, load_profile_config, walk_files
from guniflask.model import SqlToModelGenerator
from guniflask.errors import UsageError
from guniflask.commands import Command
from guniflask.app import create_app
from guniflask.bg_process import BgProcessRunner


def set_environ():
    home_dir = os.environ.get('GUNIFLASK_HOME')
    if home_dir is None:
        home_dir = os.getcwd()
        os.environ['GUNIFLASK_HOME'] = home_dir
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    if 'GUNIFLASK_PROJECT_NAME' not in os.environ:
        project_name = _infer_project_name(home_dir)
        if project_name:
            os.environ['GUNIFLASK_PROJECT_NAME'] = project_name
    if 'GUNIFLASK_CONF_DIR' not in os.environ:
        os.environ['GUNIFLASK_CONF_DIR'] = join(home_dir, 'conf')
    if 'GUNIFLASK_LOG_DIR' not in os.environ:
        os.environ['GUNIFLASK_LOG_DIR'] = join(home_dir, '.log')
    if 'GUNIFLASK_PID_DIR' not in os.environ:
        os.environ['GUNIFLASK_PID_DIR'] = join(home_dir, '.pid')
    if 'GUNIFLASK_ID_STRING' not in os.environ:
        os.environ['GUNIFLASK_ID_STRING'] = os.getlogin()


def _get_project_name():
    return os.environ.get('GUNIFLASK_PROJECT_NAME')


def _infer_project_name(home_dir):
    init_file = join(home_dir, '.guniflask-init.json')
    if isfile(init_file):
        try:
            with open(init_file, 'r') as f:
                data = json.load(f)
            project_name = data.get('project_name')
            if project_name and isdir(join(home_dir, project_name)):
                return project_name
        except Exception:
            pass
    for d in os.listdir(home_dir):
        if not d.startswith('.') and isfile(join(home_dir, d, 'app.py')):
            return d


class InitDb(Command):
    @property
    def name(self):
        return 'initdb'

    @property
    def syntax(self):
        return '[options]'

    @property
    def short_desc(self):
        return 'Initialize database from definition of models'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--active-profiles', dest='active_profiles', metavar='PROFILES',
                            help='active profiles (comma-separated)')
        parser.add_argument('-f', '--force', dest='force', action='store_true', default=False,
                            help='force creating all tables')

    def process_arguments(self, args):
        if args.active_profiles:
            os.environ['GUNIFLASK_ACTIVE_PROFILES'] = args.active_profiles
        os.environ.setdefault('GUNIFLASK_ACTIVE_PROFILES', 'dev')

    def run(self, args):
        project_name = _get_project_name()

        walk_modules(project_name)
        app = create_app(project_name)
        with app.app_context():
            s = app.extensions.get('sqlalchemy')
            if not s:
                raise UsageError('Not found sqlalchemy')
            db = s.db
            if args.force:
                db.drop_all()
            else:
                print("\033[33mThe tables already exist will be skipped.\033[0m")
                print("\033[33mYou can try '-f' option to force creating all tables.\033[0m")
            db.create_all()


class TableToModel(Command):
    @property
    def name(self):
        return 'table2model'

    @property
    def syntax(self):
        return '[options]'

    @property
    def short_desc(self):
        return 'Convert database tables to definition of models'

    def add_arguments(self, parser):
        parser.add_argument('--tables', dest='tables',
                            help='tables to process (comma-separated, default: all)')
        parser.add_argument('--dest', dest='dest',
                            help='where to put the models generated from database tables')
        parser.add_argument('-p', '--active-profiles', dest='active_profiles', metavar='PROFILES',
                            help='active profiles (comma-separated)')

    def process_arguments(self, args):
        if args.tables is not None:
            args.tables = args.tables.split(',')
        if args.active_profiles:
            os.environ['GUNIFLASK_ACTIVE_PROFILES'] = args.active_profiles
        os.environ.setdefault('GUNIFLASK_ACTIVE_PROFILES', 'dev')

    def run(self, args):
        project_name = _get_project_name()

        app = create_app(project_name)
        with app.app_context():
            settings = app.extensions['settings']
            s = app.extensions.get('sqlalchemy')
            if not s:
                raise UsageError('Not found sqlalchemy')
            db = s.db
            engine = db.engine

            dest = []
            default_dest = join(project_name, 'models')
            if args.tables:
                config_dest = args.dest
                if config_dest is None:
                    config_dest = settings.get('table2model_dest')
                if not isinstance(config_dest, str):
                    config_dest = default_dest
                dest.append({'tables': args.tables, 'dest': config_dest})
            else:
                config_dest = args.dest
                if config_dest is None:
                    config_dest = settings.get('table2model_dest', default_dest)
                if isinstance(config_dest, str):
                    dest.append({'tables': None, 'dest': config_dest})
                else:
                    for d in config_dest:
                        t = d.get('tables')
                        if isinstance(t, str):
                            t = t.split(',')
                        dest.append({'tables': t, 'dest': d.get('dest', default_dest)})

            for d in dest:
                metadata = MetaData(engine)
                metadata.reflect(only=d.get('tables'))
                gen = SqlToModelGenerator(project_name, metadata)
                gen.render(join(settings['home'], d.get('dest')))


class Debug(Command):
    @property
    def name(self):
        return 'debug'

    @property
    def short_desc(self):
        return 'Debug application'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--daemon', dest='daemon', action='store_true', help='run in daemon mode')
        parser.add_argument('-p', '--active-profiles', dest='active_profiles', metavar='PROFILES',
                            help='active profiles (comma-separated)')

    def process_arguments(self, args):
        if args.active_profiles:
            os.environ['GUNIFLASK_ACTIVE_PROFILES'] = args.active_profiles
        os.environ['GUNIFLASK_DEBUG'] = '1'
        os.environ.setdefault('GUNIFLASK_ACTIVE_PROFILES', 'dev')

    def run(self, args):
        app = GunicornApplication()
        if args.daemon:
            app.set_option('daemon', True)
        pid = get_pid(app.options)
        if pid is not None and is_started(pid):
            print('Application is already started')
            self.exitcode = 1
        else:
            app.run()


class Start(Command):
    @property
    def name(self):
        return 'start'

    @property
    def short_desc(self):
        return 'Start application'

    def add_arguments(self, parser):
        parser.add_argument('--daemon-off', dest='daemon_off', action='store_true', help='turn off daemon mode')
        parser.add_argument('-p', '--active-profiles', dest='active_profiles', metavar='PROFILES',
                            help='active profiles (comma-separated)')

    def process_arguments(self, args):
        if args.active_profiles:
            os.environ['GUNIFLASK_ACTIVE_PROFILES'] = args.active_profiles
        os.environ.setdefault('GUNIFLASK_ACTIVE_PROFILES', 'prod')

    def run(self, args):
        app = GunicornApplication()
        if args.daemon_off:
            app.set_option('daemon', False)
        pid = get_pid(app.options)
        if pid is not None and is_started(pid):
            print('Application is already started')
            self.exitcode = 1
        else:
            app.run()


class Stop(Command):
    @property
    def name(self):
        return 'stop'

    @property
    def short_desc(self):
        return 'Stop application'

    def run(self, args):
        app = GunicornApplication()
        pid = get_pid(app.options)
        if pid is None or not is_started(pid):
            print('No application to stop')
            self.exitcode = 1
        else:
            print('kill {}'.format(pid))
            os.kill(pid, signal.SIGTERM)
            time.sleep(3)
            try:
                os.kill(pid, 0)
            except OSError:
                pass
            else:
                print('Application did not stop gracefully after 3 seconds')
                print('kill -9 {}'.format(pid))
                os.kill(pid, signal.SIGKILL)


class GunicornApplication(Application):
    known_settings = {'bg_process'}

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
        return create_app(_get_project_name())

    def _make_options(self):
        pid_dir = os.environ['GUNIFLASK_PID_DIR']
        log_dir = os.environ['GUNIFLASK_LOG_DIR']
        id_string = os.environ['GUNIFLASK_ID_STRING']
        project_name = _get_project_name()
        options = {
            'daemon': True,
            'preload_app': True,
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
        # bg process
        self._set_bg_process(options)
        return options

    def _set_bg_process(self, options):
        if 'bg_process' in options:
            bg_cls = options['bg_process']
            kwargs = dict(name=_get_project_name(), bg_cls=bg_cls, on_starting=options.get('on_starting'))
            bg_runner = BgProcessRunner(**kwargs)
            options['on_starting'] = bg_runner.start
            options.pop('bg_process')

    def _make_profile_options(self, active_profiles):
        conf_dir = os.environ['GUNIFLASK_CONF_DIR']
        gc = load_profile_config(conf_dir, 'gunicorn', profiles=active_profiles)
        settings = {}
        snames = set([i.name for i in KNOWN_SETTINGS])
        snames.update(self.known_settings)
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
            'preload_app': False,
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


def get_pid(options):
    pidfile = options.get('pidfile')
    if isfile(pidfile):
        with open(pidfile, 'r') as f:
            line = f.readline()
            if line:
                pid = line.strip()
                if pid:
                    return int(pid)


def is_started(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _get_commands_from_module():
    d = {}
    for cmd in globals().values():
        if isinstance(cmd, type) and issubclass(cmd, Command):
            o = cmd()
            if o.name:
                d[o.name] = o
    return d


def _print_commands():
    print("Usage: guniflask-manage <command> [options] [args]\n")
    print("Available commands:")
    cmds = _get_commands_from_module()
    for cmdname, cmdclass in sorted(cmds.items()):
        print("   {:<13} {}".format(cmdname, cmdclass.short_desc))
    print()
    print('Use "guniflask-manage <command> -h" to see more info about a command')


def _print_unknown_command(cmdname):
    print("Unknown command: %s\n" % cmdname, file=sys.stderr)
    print('Use "guniflask-manage" to see available commands', file=sys.stderr)


def main(argv=None):
    set_environ()
    if argv is None:
        argv = sys.argv
    cmds = _get_commands_from_module()
    cmdname = argv[1] if len(argv) > 1 else None
    if not cmdname or cmdname in ('-h', '--help'):
        _print_commands()
        sys.exit(0)
    elif cmdname not in cmds:
        _print_unknown_command(cmdname)
        sys.exit(2)
    del argv[1]
    cmd = cmds[cmdname]
    parser = argparse.ArgumentParser()
    parser.usage = "manage {} {}".format(cmdname, cmd.syntax)
    parser.description = cmd.long_desc
    cmd.add_arguments(parser)
    try:
        args = parser.parse_args(args=argv[1:])
        cmd.process_arguments(args)
        cmd.run(args)
    except UsageError as e:
        print('Error: {}'.format(e), file=sys.stderr)
        sys.exit(2)
    else:
        if cmd.exitcode:
            sys.exit(cmd.exitcode)


if __name__ == '__main__':
    main()
