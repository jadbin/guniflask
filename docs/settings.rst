.. _settings:

Application Settings
====================

Uppercase Settings
------------------

定义的uppercase形式的配置项，如 ``SQLALCHEMY_DATABASE_URI`` ，会被认为是Flask相关的配置项，并在init app之前自动注入到 ``app.config`` 中。

Getting Settings
----------------

我们可以通过如下方式获取项目配置:

.. code-block:: python

    from foo import config

在 ``config.settings`` 中存放着项目所有的配置项， ``config.settings`` 是一个实现了 ``MutableMapping`` 接口的对象。
我们可以通过 ``config.setings['key']`` 的方式获取配置项 ``key`` 的属性值，如果 ``key`` 不存在则返回 ``None`` 。

Built-in Settings
-----------------

.. _active_profiles:

active_profiles
^^^^^^^^^^^^^^^

- Default: ``None``

激活哪些profile。

也可以通过环境变量 ``GUNIFLASK_ACTIVE_PROFILES`` 进行设置。

有关使用profile区别运行环境并加载不同配置的详细信息请参考 :ref:`profile` 。

cors
^^^^

- Default: ``None``

跨域相关配置。

如果为 ``True`` 表示开启跨域。
项目基于Flask-Cors实现跨域，``cors`` 也可以设置为 ``dict`` 类型，并用作传入对跨域进行详细配置的关键字参数。
详细配置可参考Flask-Cors文档: https://flask-cors.readthedocs.io/en/latest/api.html 。

.. _table2model_dest:

table2model_dest
^^^^^^^^^^^^^^^^

- Default: ``'foo/models'``

配置table2model生成结果存储的路径。

路径为相对于项目根目录的相对路径，并且需要路径对应的文件夹已经存在。
