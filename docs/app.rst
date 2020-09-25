.. _app:

Application
===========

在 ``foo.app`` 模块中我们定义应用运行所需的Flask插件，同时提供若干钩子函数，会在项目运行生命周期的不同阶段进行调用。
系统自动生成的插件会自动完成初始化操作，我们额外引入的插件需要在 :func:`~foo.app.init_app` 中实现初始化。

make_settings
-------------

.. function:: foo.app.make_settings(app, settings)

    :param app: Flask app
    :param settings: 项目配置

此函数会在读取完配置文件后进行调用。

init_app
--------

.. function:: foo.app.init_app(app, settings)

    :param app: Flask app
    :param settings: 项目配置

此函数可用于初始化Flask和及其扩展。
