.. _debug:

Debugging Application
=====================

Debug Mode
----------

在项目开发过程中，推荐以debug模式启动项目:

.. code-block:: bash

    $ bash bin/manage debug

在debug模式中会设置如下环境变量:

.. code-block:: bash

    export GUNIFLASK_DEBUG=1

我们在代码中可以根据是否设置了 ``GUNIFLASK_DEBUG`` 环境变量来确定项目是否以debug模式启动。

Debug Settings
--------------

以debug模式启动项目时，会强制设定如下gunicorn配置项:

- accesslog : ``'-'``
- errorlog : ``'-'``
- loglevel : ``'debug'``
- reload : ``True``
- reload_extra_files : conf 文件夹下的所有文件
- workers: ``1``
- daemon: ``False``

此时，我们在配置文件中对这些项的设定将不起作用。
特别的，对于reload_extra_files会合并默认配置和自定义的配置。

gunicorn配置项的详情可参考gunicorn文档: http://docs.gunicorn.org/en/stable/settings.html 。

Auto Reloading
--------------

以debug模式启动项目时，如果 ``foo`` 模块中或 conf 文件夹中的代码发生了改变，app进程会自动重启并加载最新的代码。

.. note::

    如果我们更改的是gunicorn配置项，则需要手动重启项目才会重新加载最新的gunicorn配置项。
