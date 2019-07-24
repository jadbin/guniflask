# coding=utf-8

import re
import sys
from os.path import join, dirname
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

with open(join(dirname(__file__), 'README.rst'), 'r', encoding='utf-8') as fd:
    long_description = fd.read()


def read_version():
    p = join(dirname(__file__), 'guniflask', '__init__.py')
    with open(p, 'r', encoding='utf-8') as f:
        return re.search(r"__version__ = '([^']+)'", f.read()).group(1)


def read_requirements(file):
    with open(join(dirname(__file__), 'requirements', file), 'r', encoding='utf-8') as f:
        return [l.strip() for l in f]


class PyTest(TestCommand):
    def run_tests(self):
        import pytest

        errno = pytest.main(['tests'])
        sys.exit(errno)


tests_require = read_requirements('test.txt')
app_require = read_requirements('app.txt')
install_requires = ['Jinja2>=2.10']
extras_require = {
    'app': app_require
}


def main():
    if sys.version_info < (3, 5):
        raise RuntimeError("The minimal supported Python version is 3.5")

    setup(
        name="guniflask",
        version=read_version(),
        url="https://github.com/jadbin/guniflask",
        description="flask + gunicorn, scaffolding tool for web services",
        long_description=long_description,
        author="jadbin",
        author_email="jadbin.com@hotmail.com",
        license="Apache 2",
        zip_safe=False,
        packages=find_packages(exclude=("tests",)),
        include_package_data=True,
        entry_points={
            "console_scripts": ["guniflask = guniflask.cli:main",
                                "guniflask-manage = guniflask.manage:main"]
        },
        python_requires='>=3.5',
        install_requires=install_requires,
        tests_require=tests_require,
        extras_require=extras_require,
        cmdclass={"test": PyTest},
        classifiers=[
            "License :: OSI Approved :: Apache Software License",
            "Intended Audience :: Developers",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Topic :: Software Development :: Libraries :: Python Modules"
        ]
    )


if __name__ == "__main__":
    main()
