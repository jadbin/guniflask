=========
guniflask
=========

.. image:: https://travis-ci.org/jadbin/guniflask.svg?branch=master
    :target: https://travis-ci.org/jadbin/guniflask

.. image:: https://coveralls.io/repos/github/jadbin/guniflask/badge.svg?branch=master
    :target: https://coveralls.io/github/jadbin/guniflask?branch=master

.. image:: https://img.shields.io/badge/license-Apache 2-blue.svg
    :target: https://github.com/jadbin/guniflask/blob/master/LICENSE

Overview
========

guniflask是自动化生成基于flask + gunicorn的服务端项目基础代码的构建工具。

Installation
============

guniflask需要Python 3.5或更高版本的环境支持。

可以通过pip安装或升级guniflask::

    $ pip install -U guniflask

Getting Started
===============

新建一个空文件夹 ``foo`` 并进入到 ``foo`` 中运行guniflask::

    $ mkdir foo && cd foo
    $ guniflask init

当出现提示时按 ``Enter`` 键即可选择默认设置。
提示项目创建成功后，安装项目所需依赖::

    $ pip install -U guniflask[app]

调试模式启动项目::

    $ bash bin/manage debug

在浏览器中访问 http://localhost:8000/hello-world 。

Documentation
=============

https://guniflask.readthedocs.io/
