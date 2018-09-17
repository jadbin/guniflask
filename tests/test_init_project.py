# coding=utf-8

import os
from os.path import join, exists
import subprocess
import time
import signal
from threading import Thread


def init_project(proj_dir):
    res = subprocess.run("guniflask version && cd '{}' && echo '\n\n' | guniflask init".format(proj_dir), shell=True)
    assert res.returncode == 0


def run_tests_of_project(proj_dir):
    res = subprocess.run("cd '{}' && pytest tests".format(proj_dir, proj_dir),
                         shell=True)
    assert res.returncode == 0


def run_debug_of_project(proj_dir):
    res = subprocess.run("cd '{}' && . bin/some-project-config.sh && echo $GUNIFLASK_ID_STRING".format(proj_dir),
                         shell=True, stdout=subprocess.PIPE)
    assert res.returncode == 0
    id_string = res.stdout.decode().strip()
    pid_file = join(proj_dir, '.pid', 'some-project-' + id_string + '.pid')
    t = ExceptionThread(target=kill_process, args=(pid_file,))
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


def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def kill_process(pid_file):
    t = 10
    while t > 0 and not exists(pid_file):
        t -= 1
        time.sleep(1)
    assert t > 0
    with open(pid_file, 'rb') as f:
        pid = int(f.read().decode())
    assert check_pid(pid) is True
    os.kill(pid, signal.SIGTERM)
    t = 10
    while t > 0 and exists(pid_file):
        t -= 1
        time.sleep(1)
    assert t > 0


def test_init_project(tmpdir):
    proj_dir = join(str(tmpdir), 'some_project')
    os.mkdir(proj_dir)

    init_project(proj_dir)
    run_tests_of_project(proj_dir)
    run_debug_of_project(proj_dir)
    run_initdb_without_db(proj_dir)
    run_table2model_without_db(proj_dir)
