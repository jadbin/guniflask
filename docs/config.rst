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

我们可以在 conf/gunicorn.py 中通过定义变量的方式添加gunicorn配置项，包括:

- bind: 项目运行时绑定的地址

gunicorn详细的配置项可参考gunicorn文档: http://docs.gunicorn.org/en/stable/settings.html 。

Application Config
------------------

我们在 conf/foo.py 中通过定义变量的方式添加配置项，包括用户自定义配置。

有关配置项的获取、内置配置项等详细信息可参考 :ref:`settings` 。

.. _profile:

Multiple Profiles
-----------------

在实际开发过程中，根据运行环境的不同我们可能需要不同的配置文件。
例如，在生产环境中和开发环境数据库相关的配置往往不同。

我们通过引入profile的概念来区别不同的运行环境。
例如，我们设定两个profile——prod和dev，分别对应生产环境和开发环境。
那么我们可以在 conf/foo_prod.py 中声明生产环境下的项目配置，在 conf/foo_dev.py 中声明开发环境下的项目配置。
gunicorn配置同样可以用多个profile加以区分， conf 目录下配置文件的组织形式如下:

.. code-block:: text

    conf/
        foo.py
        foo_dev.py
        foo_prod.py
        gunicorn.py
        gunicorn_dev.py
        gunicorn_prod.py

在项目中我们通过配置 :ref:`active_profiles` 来设定激活哪些profile，被激活的profile对应的配置文件会在项目运行时自动加载。
例如， ``active_profiles=prod`` 表示激活prod对应的profile。
如果同时激活多个profile，多个profile之间以 ``,`` 隔开。
例如， ``active_profiles=prod,redis`` 表示同时激活prod和redis对应的profile。
:ref:`active_profiles` 会同时作用于gunicorn配置和项目配置。

.. note::
    - :ref:`active_profiles` 只可在 conf/foo.py 中配置，在profile后缀的配置文件中配置无效。
    - 指定profile的配置文件的优先级高于未指定profile的优先级。
    - 在 :ref:`active_profiles` 中越靠左边的profile优先级越高。