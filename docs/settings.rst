.. _settings:

Application Settings
====================

Uppercase Settings
------------------

定义的uppercase形式的配置项，如 ``SQLALCHEMY_DATABASE_URI`` ，会被认为是Flask相关的配置项，并在init app之前自动注入到 ``app.config`` 中。

Getting Settings
----------------

项目在 ``${project}.settings`` 模块中声明了全局的 ``settings`` 对象，用来获取项目配置。
``settings`` 是一个实现了 ``MutableMapping`` 接口的对象。

在项目中我们可以通过如下方式获取 ``settings`` 对象:

.. code-block:: python

    from proj.settings import settings

我们可以通过 ``setings['key']`` 的方式获取配置项 ``key`` 的属性值，如果 ``key`` 不存在则返回 ``None`` 。

Built-in Settings
-----------------

.. _active_profiles:

active_profiles
^^^^^^^^^^^^^^^

- Default: ``None``

激活哪些profile。

有关profile的详细信息请参考 :ref:`profile` 。

cors
^^^^

- Default: ``None``

跨域相关配置。

如果为 ``True`` 表示开启跨域。
项目基于Flask-Cors实现跨域，``cors`` 也可以设置为 ``dict`` 类型，并用作传入对跨域进行详细配置的关键字参数。
详细配置可参考Flask-Cors文档: https://flask-cors.readthedocs.io/en/latest/api.html 。
