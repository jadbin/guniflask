.. _hook:

Hook Functions
==============

在项目的 ``hooks`` 模块中定义了若干钩子函数，会在项目运行生命周期的不同阶段进行调用。

make_settings
-------------

.. function:: hooks.make_settings(app, config):

    :param app: Flask app
    :param config: config module

此函数会在读取完配置文件后，init app之前进行调用。
