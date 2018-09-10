# coding=utf-8

import os
from os.path import exists, join, abspath, isdir, basename, dirname
from shutil import copymode, ignore_patterns

from jinja2 import Template

from guniflask.errors import AbortedError
from guniflask.utils import string_lowercase_underscore, string_uppercase_underscore, string_lowercase_hyphen

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
    default = None
    desc = None

    def __init__(self):
        self.value = self.default
        self.title = self.desc
        self.remark = self.default

    def process_arguments(self, args):
        pass

    def process_user_input(self, user_input):
        pass


class BaseNameStep(Step):
    desc = 'What is the base name of your application?'

    def process_arguments(self, args):
        project_dir = abspath(args.root_dir or '')
        self.remark = string_lowercase_underscore(basename(project_dir))

    def process_user_input(self, user_input):
        project_basename = string_lowercase_underscore(user_input)
        if not project_basename:
            project_basename = self.remark
        if project_basename and not str.isdigit(project_basename[0]):
            self.value = project_basename
            return {'project_name': project_basename}


class PortStep(Step):
    default = 8000
    desc = 'Would you like to run your application on which port?'

    def process_user_input(self, user_input):
        user_input = user_input.strip()
        if user_input:
            port = self.parse_port(user_input)
        else:
            port = self.parse_port(self.remark)
        if port is not None:
            self.value = port
            return {'port': port}

    @staticmethod
    def parse_port(port):
        try:
            res = int(port)
        except (ValueError, TypeError):
            pass
        else:
            if 0 <= res < 65535:
                return res


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
                step.process_arguments(args)
                while True:
                    self.print_request('({}/{}) {}'.format(cur_step, total_steps, step.title),
                                       step.remark)
                    user_input = input()
                    res = step.process_user_input(user_input)
                    if res is None:
                        self.print_go_back_line()
                        continue
                    settings.update(res)
                    self.print_go_back_line()
                    self.print_decision('({}/{}) {}'.format(cur_step, total_steps, step.title),
                                        step.value)
                    cur_step += 1
                    break
        except KeyboardInterrupt:
            print(flush=True)
            return
        try:
            self.copy_files(settings)
        except (KeyboardInterrupt, AbortedError):
            print(flush=True)
            self.print_aborted_error('Process is aborted by user.')
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
        if not exists(dst):
            os.makedirs(dst, 0o755)
        copymode(src, dst)
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
                            copymode(src_path, dst_path)
                        else:
                            self.print_copying_file('conflict', dst_rel_path)
                            while True:
                                self.print_request('Overwrite {}?'.format(dst_rel_path), 'Y/n/a/x')
                                user_input = input()
                                user_input = user_input.strip().lower()
                                if not user_input:
                                    user_input = 'y'
                                if user_input[0] not in 'ynax':
                                    self.print_invalid_command()
                                    self.print_go_back_line()
                                    continue
                                user_input = user_input[0]
                                self.print_clean_line()
                                self.print_go_back_line()
                                self.print_decision('Overwrite {}?'.format(dst_rel_path), user_input)
                                if user_input == 'y' or user_input == 'a':
                                    self.print_copying_file('force', dst_rel_path)
                                    self.write_file(dst_path, content)
                                    copymode(src_path, dst_path)
                                    if user_input == 'a':
                                        self.force = True
                                elif user_input == 'n':
                                    self.print_copying_file('skip', dst_rel_path)
                                elif user_input == 'x':
                                    raise AbortedError
                                break
                else:
                    self.print_copying_file('create', dst_rel_path)
                    self.write_file(dst_path, content)
                    copymode(src_path, dst_path)

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
        with open(path, 'w', encoding='utf-8') as f:
            f.write(raw)

    @staticmethod
    def render_string(raw, **kwargs):
        return Template(raw, keep_trailing_newline=True).render(**kwargs)

    @staticmethod
    def print_request(question, option):
        print('\033[32;40m?\033[0m {} \033[37;40m({})\033[0m '
              .format(question, option), end='', flush=True)

    @staticmethod
    def print_decision(question, decision):
        print('\033[32;40m?\033[0m {} \033[36;40m{}\033[0m'
              .format(question, decision), flush=True)

    @staticmethod
    def print_welcome(project_dir):
        print('\033[37;40mWelcome to gunicorn generator\033[0m \033[33;40mv{}\033[0m'
              .format(__version__), flush=True)
        print('\033[37;40mApplication file will be created in folder:\033[0m \033[33;40m{}\033[0m'
              .format(project_dir), flush=True)

    @staticmethod
    def print_go_back_line():
        print('\033[1A\r\033[K', end='', flush=True)

    @staticmethod
    def print_clean_line():
        print('\r\033[K', end='', flush=True)

    @staticmethod
    def print_invalid_command():
        print('\033[31;40m>>\033[0m Please enter a valid command', end='', flush=True)

    @staticmethod
    def print_success():
        print('\033[32;40mApplication is created successfully.\033[0m', flush=True)

    @staticmethod
    def print_aborted_error(message):
        print('\033[33;40m{}\033[0m'.format(message), flush=True)

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
        print('\033[{};40m{:>9}\033[0m {}'.format(color, t, path), flush=True)


class VersionCommand(Command):
    @property
    def name(self):
        return "version"

    @property
    def short_desc(self):
        return "Print the version"

    def run(self, args):
        print("guniflask version {}".format(__version__))
