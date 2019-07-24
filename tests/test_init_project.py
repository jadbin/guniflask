# coding=utf-8

import os
from os.path import join, exists
import subprocess
import time
from threading import Thread
import json

from guniflask import __version__


def show_version():
    res = subprocess.run("guniflask version", shell=True)
    assert res.returncode == 0


def init_project(proj_dir):
    settings = {
        'guniflask_version': __version__,
        'authentication_type': None,
        'port': 8000,
        'project_name': 'foo'
    }
    with open(join(proj_dir, '.guniflask-init.json'), 'w') as f:
        json.dump(settings, f)
    res = subprocess.run("cd '{}' && guniflask init".format(proj_dir),
                         shell=True)
    assert res.returncode == 0


def run_tests_of_project(proj_dir):
    res = subprocess.run("cd '{}' && pytest tests".format(proj_dir, proj_dir),
                         shell=True)
    assert res.returncode == 0


def run_debug_of_project(proj_dir):
    res = subprocess.run("cd '{}' && . bin/app-config.sh && echo $GUNIFLASK_ID_STRING".format(proj_dir),
                         shell=True, stdout=subprocess.PIPE)
    assert res.returncode == 0
    id_string = res.stdout.decode().strip()
    pid_file = join(proj_dir, '.pid', 'foo-' + id_string + '.pid')
    t = ExceptionThread(target=stop_project, args=(pid_file, proj_dir))
    t.start()
    res = subprocess.run("cd '{}' && bash bin/manage debug".format(proj_dir), shell=True)
    assert res.returncode == 0
    t.join()
    assert len(t.bucket) == 0, 'Exception in thread'


def run_table2model_without_db(proj_dir):
    res = subprocess.run("cd '{}' && bash bin/manage table2model".format(proj_dir), shell=True)
    assert res.returncode == 2


def run_initdb_without_db(proj_dir):
    res = subprocess.run("cd '{}' && bash bin/manage initdb -f".format(proj_dir), shell=True)
    assert res.returncode == 2


class ExceptionThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bucket = []

    def run(self):
        try:
            super().run()
        except Exception as e:
            self.bucket.append(e)
            raise


def stop_project(pid_file, proj_dir):
    t = 10
    while t > 0 and not exists(pid_file):
        t -= 1
        time.sleep(1)
    assert t > 0, 'no project to stop'
    time.sleep(3)
    res = subprocess.run("cd '{}' && bash bin/manage stop".format(proj_dir), shell=True)
    assert res.returncode == 0
    t = 10
    while t > 0 and exists(pid_file):
        t -= 1
        time.sleep(1)
    assert t > 0, 'did not stop gracefully'


def test_init_project(tmpdir, monkeypatch):
    proj_dir = join(str(tmpdir), 'foo')
    os.mkdir(proj_dir)
    show_version()
    init_project(proj_dir)
    # run_tests_of_project(proj_dir)
    run_debug_of_project(proj_dir)
    run_initdb_without_db(proj_dir)
    run_table2model_without_db(proj_dir)
