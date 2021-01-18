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
install_requires = [
    'Flask>=1.1.2',
    'SQLAlchemy>=1.3.22',
    'Flask-Cors>=3.0.10',
    'PyJWT>=2.0.0',
    'APScheduler>=3.6.3',
    'requests>=2.25.1',
    'dnspython>=2.1.0',
    'python-dotenv>=0.15.0',
]


def main():
    if sys.version_info < (3, 6):
        raise RuntimeError("The minimal supported Python version is 3.6")

    setup(
        name="guniflask",
        version=read_version(),
        url="https://github.com/jadbin/guniflask",
        description="Better coding experience for Flask",
        long_description=long_description,
        author="jadbin",
        author_email="jadbin.com@hotmail.com",
        license="MIT",
        zip_safe=False,
        packages=find_packages(exclude=("tests",)),
        include_package_data=True,
        python_requires='>=3.6',
        install_requires=install_requires,
        tests_require=tests_require,
        cmdclass={"test": PyTest},
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Intended Audience :: Developers",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries :: Application Frameworks",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ]
    )


if __name__ == "__main__":
    main()
