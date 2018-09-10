.. _config:

Configuration
=============

Overview
--------

配置包括两部分，一部分是gunicorn配置，另一部分是项目配置。
gunicorn配置主要是对HTTP Server的配置。
项目配置主要是业务相关的配置。

Gunicorn Config
---------------

我们可以在 conf/gunicorn.py 中通过定义变量的方式添加gunicorn配置项。

gunicorn详细的配置项可参考gunicorn文档: http://docs.gunicorn.org/en/stable/settings.html 。

Application Config
------------------

我们有两种途径声明项目的配置项，以及用户自定义的配置。
第一个途径是在 ``${proj}.config`` 模块中通过定义变量的方式添加配置项。
第二个途径是在 conf/``${proj}.py`` 中通过定义变量的方式添加配置项。

项目配置的优先级由低到高为:

1. ${proj}/config.py
#. conf/${proj}.py

如果配置存在冲突，高优先级配置会覆盖低优先级配置。

更多有关项目配置项的信息可参考 :ref:`settings` 。

.. _profile:

Multiple Profiles
-----------------

在实际开发过程中，根据运行环境的不同我们可能需要不同的配置文件。
例如，在生产环境中和开发环境数据库相关的配置往往不同。

我们通过引入profile的概念来区别不同的运行环境。
例如，我们设定两个profile——prod和dev，分别对应生产环境和开发环境。
那么我们可以在 conf/${proj}_prod.py 中声明生产环境下的项目配置，在 conf/${proj}_dev.py 中声明开发环境下的项目配置。
gunicorn配置同样可以用多个profile加以区分， conf 目录下配置文件的组织形式如下:

.. code-block:: text

    conf/
        ${proj}.py
        ${proj}_dev.py
        ${proj}_prod.py
        gunicorn.py
        gunicorn_dev.py
        gunicorn_prod.py

在项目中我们通过配置 :ref:`active_profiles` 来设定激活哪些profile，被激活的profile对应的配置文件会在项目运行时自动加载。
例如， ``active_profiles=prod`` 表示激活prod对应的profile。
如果同时激活多个profile，多个profile之间以 ``,`` 隔开。
例如， ``active_profiles=prod,redis`` 表示同时激活prod和redis对应的profile。

:ref:`active_profiles` 只可在 conf/${proj}.py 或 ${proj}/config.py 中进行配置，会同时作用于gunicorn配置和项目配置。

.. note::

    - 指定profile的配置文件的优先级高于未指定profile的优先级。
    - 在 :ref:`active_profiles` 中越靠左边的profile优先级越高。
