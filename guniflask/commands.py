# coding=utf-8

import os
from os.path import exists, join, abspath, isdir, basename, dirname
from shutil import ignore_patterns

from jinja2 import Template

from guniflask.errors import AbortedError
from guniflask.utils.template import string_lowercase_underscore, string_lowercase_hyphen
from guniflask.utils.config import load_config
from guniflask import __version__


class Command:
    def __init__(self):
        self.exitcode = 0

    @property
    def name(self):
        return ""

    @property
    def syntax(self):
        return ""

    @property
    def short_desc(self):
        return ""

    @property
    def long_desc(self):
        return self.short_desc

    def add_arguments(self, parser):
        pass

    def process_arguments(self, args):
        pass

    def run(self, args):
        raise NotImplementedError


class Step:
    desc = None

    def __init__(self):
        self.value = None
        self.title = self.desc
        self.tooltip = None

    def process_arguments(self, args, settings):
        pass

    def process_user_input(self):
        while True:
            self.show_question()
            user_input = self.get_user_input()
            if self.check_user_input(user_input):
                self.show_decision()
                break
            else:
                self.show_invalid_tooltip()

    def show_question(self):
        raise NotImplementedError

    def get_user_input(self):
        raise NotImplementedError

    def show_decision(self):
        raise NotImplementedError

    def show_invalid_tooltip(self):
        raise NotImplementedError

    def check_user_input(self, user_input):
        return True

    def update_settings(self, settings):
        raise NotImplementedError

    def question(self):
        return '\033[32m?\033[0m {} \033[37m({})\033[0m'.format(self.title, self.tooltip)

    def decision(self):
        return '\033[32m?\033[0m {} \033[36m{}\033[0m'.format(self.title, self.value)

    def go_back_lines(self, n=1):
        return '\033[1A\r\033[K' * n

    def clean_line(self):
        return '\r\033[K'


class InputStep(Step):
    def show_question(self):
        print(self.question() + ' ', end='', flush=True)

    def get_user_input(self):
        return input()

    def show_decision(self):
        print(self.clean_line(), end='', flush=True)
        print(self.go_back_lines(), end='', flush=True)
        print(self.decision(), flush=True)

    def show_invalid_tooltip(self):
        print(self.go_back_lines(), end='', flush=True)


class BaseNameStep(InputStep):
    desc = 'What is the base name of your application?'

    def process_arguments(self, args, settings):
        project_dir = abspath(args.root_dir or '')
        self.tooltip = string_lowercase_underscore(basename(project_dir))
        conf_dir = join(project_dir, 'conf')
        if isdir(conf_dir):
            names = os.listdir(conf_dir)
            for name in names:
                if name.endswith('.py'):
                    pname = name[:-3]
                    if isdir(join(project_dir, pname)):
                        self.tooltip = pname

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

    def process_arguments(self, args, settings):
        project_dir = settings['project_dir']
        self.tooltip = 8000
        try:
            c = load_config(join(project_dir, 'conf', 'gunicorn.py'))
            port = self.parse_port(c['bind'].rsplit(':')[1].strip())
            if port is not None:
                self.tooltip = port
        except Exception:
            pass

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

    def run(self, args):
        steps = [BaseNameStep(), PortStep()]
        cur_step, total_steps = 1, 2
        project_dir = abspath(args.root_dir or '')
        self.print_welcome(project_dir)
        print(flush=True)
        settings = {'project_dir': project_dir}
        try:
            for step in steps:
                step.title = '({}/{}) {}'.format(cur_step, total_steps, step.title)
                step.process_arguments(args, settings)
                step.process_user_input()
                step.update_settings(settings)
                cur_step += 1
            self.copy_files(settings)
        except (KeyboardInterrupt, AbortedError):
            print(flush=True)
            self.print_aborted_error()
            self.exitcode = 1
            return
        print(flush=True)
        self.print_success()

    def copy_files(self, settings):
        templates_dir = join(dirname(__file__), 'templates', 'project')
        project_dir = settings['project_dir']
        project_name = settings['project_name']
        settings['project__name'] = string_lowercase_hyphen(project_name)

        print(flush=True)
        print('Copying files:', flush=True)
        self.force = False
        self.copytree(templates_dir, project_dir, settings)

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
                    content = self.render_string(content, **settings)
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
        return Template(raw, keep_trailing_newline=True).render(**kwargs)

    @staticmethod
    def print_welcome(project_dir):
        print('\033[37mWelcome to gunicorn generator\033[0m \033[33mv{}\033[0m'
              .format(__version__), flush=True)
        print('\033[37mApplication file will be created in folder:\033[0m \033[33m{}\033[0m'
              .format(project_dir), flush=True)

    @staticmethod
    def print_success():
        print('\033[32mApplication is created successfully.\033[0m', flush=True)

    @staticmethod
    def print_aborted_error():
        print('\033[33mProcess is aborted by user.\033[0m', flush=True)

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


class VersionCommand(Command):
    @property
    def name(self):
        return "version"

    @property
    def short_desc(self):
        return "Print the version"

    def run(self, args):
        print("guniflask version {}".format(__version__))
