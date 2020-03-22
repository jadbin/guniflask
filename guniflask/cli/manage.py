# coding=utf-8

import sys
import os
from os.path import isfile, join
import argparse
import signal
import time
from collections import defaultdict

from sqlalchemy.schema import MetaData

from guniflask.utils.env import walk_modules
from guniflask.model.sqlgen import SqlToModelGenerator
from guniflask.cli.errors import UsageError
from guniflask.cli.command import Command
from guniflask.app import create_app
from guniflask.gunicorn import GunicornApplication
from guniflask.utils.process import pid_exists
from guniflask.cli.env import set_default_env, get_project_name_from_env


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
        project_name = get_project_name_from_env()

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
        parser.add_argument('-p', '--active-profiles', dest='active_profiles', metavar='PROFILES',
                            help='active profiles (comma-separated)')

    def process_arguments(self, args):
        if args.active_profiles:
            os.environ['GUNIFLASK_ACTIVE_PROFILES'] = args.active_profiles
        os.environ.setdefault('GUNIFLASK_ACTIVE_PROFILES', 'dev')

    def run(self, args):
        project_name = get_project_name_from_env()

        app = create_app(project_name)
        with app.app_context():
            settings = app.extensions['settings']
            s = app.extensions.get('sqlalchemy')
            if not s:
                raise UsageError('Not found SQLAlchemy')
            db = s.db
            default_dest = defaultdict(dict)
            binds = [None] + list(app.config.get('SQLALCHEMY_BINDS') or ())
            for b in binds:
                if b is None:
                    default_dest[b] = {'dest': join(project_name, 'models')}
                else:
                    default_dest[b] = {'dest': join(project_name, 'models_{}'.format(b))}
            dest_config = settings.get_by_prefix('guniflask.table2model_dest', default_dest)
            if isinstance(default_dest, str):
                default_dest[None]['dest'] = dest_config
            else:
                for b in dest_config:
                    if b not in default_dest:
                        raise UsageError('"{}" is not configured in binds'.format(b))
                    c = dest_config[b]
                    if isinstance(c, str):
                        default_dest[b]['dest'] = c
                    else:
                        default_dest[b].update(c)
            for b in default_dest:
                c = default_dest[b]
                engine = db.get_engine(bind=b)
                metadata = MetaData(engine)
                metadata.reflect()
                gen = SqlToModelGenerator(project_name, metadata, bind=b)
                gen.render(join(settings['home'], c.get('dest')))


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
        pid = _read_pid(app.options)
        if pid is not None and pid_exists(pid):
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
        pid = _read_pid(app.options)
        if pid is not None and pid_exists(pid):
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
        pid = _read_pid(app.options)
        if pid is None or not pid_exists(pid):
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


def _read_pid(options):
    pidfile = options.get('pidfile')
    if isfile(pidfile):
        with open(pidfile, 'r') as f:
            line = f.readline()
            if line:
                pid = line.strip()
                if pid:
                    return int(pid)


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
    set_default_env()
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
    parser.usage = "guniflask-manage {} {}".format(cmdname, cmd.syntax)
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
