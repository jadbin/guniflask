.. _config:

Configuration
=============

Overview
--------

配置包括两部分，一部分是gunicorn配置，另一部分是app配置。
gunicorn配置主要是对HTTP Server的配置。
app配置主要是业务相关的配置。

部分配置也可以通过环境变量设定，环境变量的优先级高于配置文件。

Gunicorn Configuration
----------------------

我们可以在 conf/gunicorn.py 中通过定义变量的方式添加gunicorn配置项，包括但不限于:

- bind: 项目运行时绑定的地址
- loglevel: 日志级别

gunicorn详细的配置项可参考gunicorn文档: http://docs.gunicorn.org/en/stable/settings.html 。

项目默认的gunicorn配置项:

- daemon: ``True``
- workers: ``os.cpu_count()``
- pidfile: 默认存放在项目根目录下的 .pid 文件夹中
- accesslog: 默认存放在项目根目录下的 .log 文件夹中
- errorlog: 默认存放在项目根目录下的 .log 文件夹中

Application Configuration
-------------------------

我们在 conf/app.env 中定义应用启动时加载的环境变量。

我们在 conf/foo.py 中通过定义变量的方式添加配置项，包括系统功能配置、项目自定义配置等。有关配置项的获取、内置配置项等详细信息可参考 :ref:`settings` 。

.. _profile:

Multiple Profiles
-----------------

在实际开发过程中，根据运行环境的不同我们可能需要不同的配置文件。
例如，在生产环境中和开发环境数据库相关的配置往往不同。

我们通过引入profile的概念来区别不同的运行环境。
例如，我们设定两个profile——prod和dev，分别对应生产环境和开发环境。
那么我们可以在 conf/foo_prod.py 中声明生产环境下的项目配置，在 conf/foo_dev.py 中声明开发环境下的项目配置。
环境变量配置和gunicorn配置同样可以用profile后缀加以区分， conf 目录下配置文件的组织形式如下:

.. code-block:: text

    conf/
        app.env
        app_dev.env
        app_prod.env
        foo.py
        foo_dev.py
        foo_prod.py
        gunicorn.py
        gunicorn_dev.py
        gunicorn_prod.py
