.. _settings:

Application Settings
====================

项目的配置项在 conf/foo.py 文件中定义。
针对不同运行环境可以通过指定profile实现项目配置的切换，详见 :ref:`profile` 。

Uppercase Settings
------------------

定义的uppercase形式的配置项，如 ``SQLALCHEMY_DATABASE_URI`` ，会被认为是Flask相关的配置项，并在init app之前自动注入到 ``app.config`` 中。

Getting Settings
----------------

我们可以通过如下方式获取项目配置:

.. code-block:: python

    from guniflask.config import settings

在 ``settings`` 中存放着项目所有的配置项， ``settings`` 是一个实现了 ``MutableMapping`` 接口的对象。
我们可以通过 ``setings['key']`` 的方式获取配置项 ``key`` 的属性值，如果 ``key`` 不存在则返回 ``None`` 。

Built-in Settings
-----------------

home
^^^^

项目根目录。

在配置文件中设置无效。

.. _active_profiles:

active_profiles
^^^^^^^^^^^^^^^

- Default: ``None``

激活哪些profile。

在配置文件中设置无效。可以通过环境变量 ``GUNIFLASK_ACTIVE_PROFILES`` 进行设置，或通过 ``manage debug/start`` 命令的 ``-p`` 选项进行设置。

有关使用profile区别运行环境并加载不同配置的详细信息请参考 :ref:`profile` 。

debug
^^^^^

- Default: ``None``

是否为debug模式。

在配置文件中设置无效。可以通过环境变量 ``GUNIFLASK_DEBUG`` 进行设置，在执行 ``manage debug`` 命令会自动设置。


Settings to Configure the Built-in Features
-------------------------------------------

我们在名为 ``guniflask`` 的dict对象下配置guniflask提供的内置功能。
可用的配置项包括：

cors
^^^^

跨域相关配置。

jwt
^^^

是否开启基于JWT的认证功能及相关配配置。

.. _table2model_dest:

table2model_dest
^^^^^^^^^^^^^^^^

- Default: ``'foo/models'``

配置table2model生成结果存储的模块路径，路径为相对于项目根目录的相对路径。
默认存储在项目根模块下的 ``models`` 模块中。

wrap_sqlalchemy_model
^^^^^^^^^^^^^^^^^^^^^

- Default: ``True``

为SQLAlchemy的Model对象动态添加工具函数。
