# coding=utf-8

import os
from os.path import exists, join, abspath, isdir, basename, dirname
from shutil import ignore_patterns
import json
import sys
import argparse

from jinja2 import Environment

from guniflask.cli.errors import AbortedError, TemplateError, UsageError
from guniflask.utils.string import string_lowercase_underscore
from guniflask.config.template import _template_folder
from guniflask.security.jwt import JwtHelper
from guniflask import __version__
from guniflask.cli.command import Command
from guniflask.cli.step import InputStep, ChoiceStep, StepChain


class BaseNameStep(InputStep):
    desc = 'What is the base name of your application?'

    def process_arguments(self, settings):
        project_dir = settings['project_dir']
        self.tooltip = string_lowercase_underscore(basename(project_dir))
        old_settings = settings['old_settings']
        if old_settings and 'project_name' in old_settings:
            self.tooltip = old_settings['project_name']

    def check_user_input(self, user_input):
        project_basename = string_lowercase_underscore(user_input)
        if not project_basename:
            project_basename = self.tooltip
        if project_basename and not str.isdigit(project_basename[0]):
            self.value = project_basename
            return True
        return False

    def show_invalid_tooltip(self):
        print('\033[31m>>\033[0m Please input a valid project name', end='', flush=True)
        super().show_invalid_tooltip()

    def update_settings(self, settings):
        settings['project_name'] = self.value


class PortStep(InputStep):
    desc = 'Would you like to run your application on which port?'

    def process_arguments(self, settings):
        self.tooltip = 8000
        old_settings = settings['old_settings']
        if old_settings and 'port' in old_settings:
            self.tooltip = old_settings['port']

    def check_user_input(self, user_input):
        user_input = user_input.strip()
        if user_input:
            port = self.parse_port(user_input)
        else:
            port = self.parse_port(self.tooltip)
        if port is not None:
            self.value = port
            return True
        return False

    def show_invalid_tooltip(self):
        print('\033[31m>>\033[0m Please input a valid port (0 ~ 65535)', end='', flush=True)
        super().show_invalid_tooltip()

    def update_settings(self, settings):
        settings['port'] = self.value

    @staticmethod
    def parse_port(port):
        try:
            res = int(port)
        except (ValueError, TypeError):
            pass
        else:
            if 0 <= res < 65536:
                return res


class AuthenticationTypeStep(ChoiceStep):
    desc = 'Which type of authentication would you like to use?'

    def __init__(self):
        super().__init__()
        self.tooltip = 'Use arrow keys'
        self.add_choice('No authentication', None)
        self.add_choice('JWT authentication', 'jwt')

    def update_settings(self, settings):
        security = self.selected_value
        settings['authentication_type'] = security
        if self.selected_value == 'jwt':
            settings['jwt_secret'] = JwtHelper.generate_jwt_secret()


class ConflictFileStep(InputStep):
    def __init__(self, file):
        super().__init__()
        self.title = 'Overwrite {}?'.format(file)
        self.tooltip = 'Y/n/a/x'

    def check_user_input(self, user_input):
        user_input = user_input.strip().lower()
        if not user_input:
            user_input = 'y'
        if len(user_input) > 1 or user_input not in 'ynax':
            return False
        self.value = user_input
        return True

    def show_invalid_tooltip(self):
        print('\033[31m>>\033[0m Please enter a valid command', end='', flush=True)
        super().show_invalid_tooltip()


class InitCommand(Command):
    @property
    def syntax(self):
        return '[options]'

    @property
    def name(self):
        return 'init'

    @property
    def short_desc(self):
        return 'Initialize a project'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--root-dir', dest='root_dir', metavar='DIR',
                            help='application root directory')
        parser.add_argument('-f', '--force', dest='force', action='store_true', default=False,
                            help='force generating an application')

    def run(self, args):
        project_dir = abspath(args.root_dir or '')
        self.print_welcome(project_dir)
        try:
            init_json_file = join(project_dir, '.guniflask-init.json')
            old_settings = None
            try:
                with open(init_json_file, 'r', encoding='utf-8') as f:
                    old_settings = json.load(f)
                if args.force:
                    raise FileNotFoundError
                settings = old_settings
                self.print_regenerate_project()
            except (FileNotFoundError, json.JSONDecodeError):
                settings = self.get_settings_by_steps(project_dir, old_settings=old_settings)
                with open(init_json_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, sort_keys=True)
            self.copy_files(project_dir, settings)
        except (KeyboardInterrupt, AbortedError):
            print(flush=True)
            self.print_aborted_error()
            self.exitcode = 1

    def get_settings_by_steps(self, project_dir, old_settings=None):
        step_chain = StepChain(AuthenticationTypeStep()).previous(PortStep()).previous(BaseNameStep())
        settings = {'project_dir': project_dir,
                    'old_settings': old_settings,
                    'guniflask_version': __version__}
        print(flush=True)
        for cur_step, total_steps, step in step_chain:
            step.title = '({}/{}) {}'.format(cur_step, total_steps, step.title)
            step.process_arguments(settings)
            step.process_user_input()
            step.update_settings(settings)
            cur_step += 1
        del settings['project_dir']
        del settings['old_settings']
        return settings

    def copy_files(self, project_dir, settings):
        settings = dict(settings)
        settings['project_dir'] = project_dir

        print(flush=True)
        self.print_copying_files()
        self.force = False
        self.copytree(join(_template_folder, 'project'), project_dir, settings)
        print(flush=True)
        self.print_success()

    def copytree(self, src, dst, settings):
        names = os.listdir(src)
        ignored_names = ignore_patterns('*.pyc')(src, names)
        for name in names:
            if name in ignored_names:
                continue
            src_path = join(src, name)
            dst_name = self.render_string(name, **settings)
            dst_path = join(dst, dst_name)
            dst_rel_path = self.relative_path(dst_path, settings['project_dir'])

            if isdir(src_path):
                self.copytree(src_path, dst_path, settings)
            else:
                content = self.read_file(src_path)
                if dst_name.endswith('.tmpl'):
                    dst_name = dst_name[:-5]
                    dst_path = join(dst, dst_name)
                    dst_rel_path = self.relative_path(dst_path, settings['project_dir'])
                    try:
                        content = self.render_string(content, **settings)
                    except TemplateError:
                        continue
                if exists(dst_path):
                    raw = self.read_file(dst_path)
                    if content == raw:
                        self.print_copying_file('identical', dst_rel_path)
                    else:
                        if self.force:
                            self.print_copying_file('force', dst_rel_path)
                            self.write_file(dst_path, content)
                        else:
                            self.print_copying_file('conflict', dst_rel_path)
                            cf_step = ConflictFileStep(dst_rel_path)
                            cf_step.process_user_input()
                            user_input = cf_step.value
                            if user_input == 'y' or user_input == 'a':
                                self.print_copying_file('force', dst_rel_path)
                                self.write_file(dst_path, content)
                                if user_input == 'a':
                                    self.force = True
                            elif user_input == 'n':
                                self.print_copying_file('skip', dst_rel_path)
                            elif user_input == 'x':
                                raise AbortedError
                else:
                    self.print_copying_file('create', dst_rel_path)
                    self.write_file(dst_path, content)

    @staticmethod
    def relative_path(path, fpath):
        path = abspath(path)
        fpath = abspath(fpath)
        if path.startswith(fpath):
            path = path[len(fpath):]
            if path.startswith(os.path.sep):
                path = path[1:]
        return path

    @staticmethod
    def read_file(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def write_file(path, raw):
        d = dirname(path)
        if not exists(d):
            os.makedirs(d)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(raw)

    @staticmethod
    def render_string(raw, **kwargs):
        env = jinja2_env()
        return env.from_string(raw).render(**kwargs)

    @staticmethod
    def print_welcome(project_dir):
        print('\033[37mWelcome to guniflask generator\033[0m \033[33mv{}\033[0m'
              .format(__version__), flush=True)
        print('\033[37mApplication file will be created in folder:\033[0m \033[33m{}\033[0m'
              .format(project_dir), flush=True)

    @staticmethod
    def print_regenerate_project():
        print('\033[32mThis is an existing project, using the configuration from .guniflask-init.json '
              'to regenerate the project...\033[0m')

    @staticmethod
    def print_success():
        print('\033[32mApplication is created successfully.\033[0m', flush=True)

    @staticmethod
    def print_aborted_error():
        print('\033[33mProcess is aborted by user.\033[0m', flush=True)

    @staticmethod
    def print_copying_files():
        print('Copying files:', flush=True)

    @staticmethod
    def print_copying_file(t, path):
        color = 0
        if t == 'identical':
            color = 36
        elif t == 'conflict':
            color = 31
        elif t == 'create':
            color = 32
        elif t == 'force' or t == 'skip':
            color = 33
        print('\033[{}m{:>9}\033[0m {}'.format(color, t, path), flush=True)


def jinja2_env():
    def _raise_helper(message):
        if message:
            raise TemplateError(message)
        raise TemplateError

    def _assert_helper(logical, message=None):
        if not logical:
            _raise_helper(message)
        return ''

    env = Environment(keep_trailing_newline=True)
    env.globals['raise'] = _raise_helper
    env.globals['assert'] = _assert_helper
    return env


class VersionCommand(Command):
    @property
    def name(self):
        return "version"

    @property
    def short_desc(self):
        return "Print the version"

    def run(self, args):
        print("guniflask version {}".format(__version__))


def _get_commands_from_module():
    d = {}
    for cmd in globals().values():
        if isinstance(cmd, type) and issubclass(cmd, Command):
            o = cmd()
            if o.name:
                d[o.name] = o
    return d


def _print_commands():
    print("Usage: guniflask <command> [options] [args]\n")
    print("Available commands:")
    cmds = _get_commands_from_module()
    for cmdname, cmdclass in sorted(cmds.items()):
        print("  {:<10} {}".format(cmdname, cmdclass.short_desc))
    print()
    print('Use "guniflask <command> -h" to see more info about a command')


def _print_unknown_command(cmdname):
    print("Unknown command: %s\n" % cmdname)
    print('Use "guniflask" to see available commands')


def main(argv=None):
    if argv is None:
        argv = sys.argv
    cmds = _get_commands_from_module()
    cmdname = argv[1] if len(argv) > 1 else None
    if not cmdname:
        _print_commands()
        sys.exit(0)
    elif cmdname not in cmds:
        _print_unknown_command(cmdname)
        sys.exit(2)
    del argv[1]
    cmd = cmds[cmdname]
    parser = argparse.ArgumentParser()
    parser.usage = "guniflask {} {}".format(cmdname, cmd.syntax)
    parser.description = cmd.long_desc
    cmd.add_arguments(parser)
    try:
        args = parser.parse_args(args=argv[1:])
        cmd.process_arguments(args)
        cmd.run(args)
    except UsageError as e:
        if e.print_help:
            parser.print_help(sys.stderr)
        print('Error: {}'.format(e), file=sys.stderr)
        sys.exit(2)
    else:
        if cmd.exitcode:
            sys.exit(cmd.exitcode)
