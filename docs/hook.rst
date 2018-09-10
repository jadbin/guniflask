.. _hook:

Hook Functions
==============

在 ``${proj}.config`` 模块中我们还可以定义如下的若干钩子函数，会在项目运行生命周期的不同阶段进行调用。

make_settings
-------------

.. function:: ${proj}.config.make_settings(app, settings):

    :param app: Flask app
    :param config: 项目配置

此函数会在读取完配置文件后，init app之前进行调用。

init_app
--------

.. function:: ${proj}.config.init_app(app, settings):

    :param app: Flask app
    :param config: 项目配置

此函数会在项目使用的Flask拓展init app之后，运行app之前进行调用。
