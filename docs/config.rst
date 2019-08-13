.. _config:

Configuration
=============

Overview
--------

配置包括两部分，一部分是gunicorn配置，另一部分是app配置。
gunicorn配置主要是对HTTP Server的配置。
app配置主要是业务相关的配置。

部分配置也可以通过环境变量设定，环境变量的优先级高于配置文件。

Gunicorn Config
---------------

我们可以在 conf/gunicorn.py 中通过定义变量的方式添加gunicorn配置项，包括但不限于:

- bind: 项目运行时绑定的地址
- loglevel: 日志级别

gunicorn详细的配置项可参考gunicorn文档: http://docs.gunicorn.org/en/stable/settings.html 。

项目默认的gunicorn配置项:

- daemon: ``True``
- preload_app: ``True``
- workers: ``multiprocessing.cpu_count()``
- worker_class: ``'gevent'``
- pidfile: 默认存放在根目录下的 .pid 文件夹中
- accesslog: 默认存放在根目录下的 .log 文件夹中
- errorlog: 默认存放在根目录下的 .log 文件夹中

以下为guniflask约定的配置:

.. _bg_process:

bg_process
^^^^^^^^^^

设置后台运行进程的class，需要继承 :class:`guniflask.bg_process.BgProcess` ，在启动gunicorn master时会启动配置的进程。

Application Config
------------------

我们在 conf/app.py 中通过定义变量的方式添加配置项，包括用户自定义配置。

有关配置项的获取、内置配置项等详细信息可参考 :ref:`settings` 。

.. _profile:

Multiple Profiles
-----------------

在实际开发过程中，根据运行环境的不同我们可能需要不同的配置文件。
例如，在生产环境中和开发环境数据库相关的配置往往不同。

我们通过引入profile的概念来区别不同的运行环境。
例如，我们设定两个profile——prod和dev，分别对应生产环境和开发环境。
那么我们可以在 conf/app_prod.py 中声明生产环境下的项目配置，在 conf/app_dev.py 中声明开发环境下的项目配置。
gunicorn配置同样可以用profile后缀加以区分， conf 目录下配置文件的组织形式如下:

.. code-block:: text

    conf/
        app.py
        app_dev.py
        app_prod.py
        gunicorn.py
        gunicorn_dev.py
        gunicorn_prod.py

在 app.py 中我们通过配置 :ref:`active_profiles` 来设定激活哪些profile，被激活的profile对应的配置文件会在项目运行时自动加载。
例如， ``active_profiles=prod`` 表示激活prod对应的profile。
如果同时激活多个profile，多个profile之间以 ``,`` 隔开。
例如， ``active_profiles=prod,redis`` 表示同时激活prod和redis对应的profile。
:ref:`active_profiles` 会同时作用于gunicorn配置和项目配置。

.. note::
    - :ref:`active_profiles` 在profile后缀的配置文件中配置无效。
    - 高优先级配置文件会覆盖低优先级配置文件中相同的配置项，指定profile的配置的优先级高于未指定profile的配置，在 :ref:`active_profiles` 中越靠左边的profile优先级越高。
