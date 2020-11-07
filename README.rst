=========
guniflask
=========

.. image:: https://travis-ci.org/jadbin/guniflask.svg?branch=master
    :target: https://travis-ci.org/jadbin/guniflask

.. image:: https://coveralls.io/repos/github/jadbin/guniflask/badge.svg?branch=master
    :target: https://coveralls.io/github/jadbin/guniflask?branch=master

.. image:: https://img.shields.io/github/license/jadbin/guniflask
    :target: https://github.com/jadbin/guniflask/blob/master/LICENSE

Overview
========

guniflask是自动化生成基于flask + gunicorn的服务端项目基础代码的构建工具。

Installation
============

guniflask需要Python 3.6或更高版本的环境支持。

可以通过pip安装或升级guniflask::

    $ pip install -U guniflask

Getting Started
===============

安装guniflask项目生成工具::

    $ pip install -U guniflask-cli

新建一个空文件夹 ``foo`` 并进入到 ``foo`` 中::

    $ mkdir foo && cd foo

运行如下命令::

    $ guniflask init

当出现提示时按 ``Enter`` 键即可选择默认设置。
提示项目创建成功后，安装项目所需依赖::

    $ pip install -r requirements/app.txt

调试模式启动项目::

    $ bash bin/manage debug

Documentation
=============

https://guniflask.readthedocs.io/
