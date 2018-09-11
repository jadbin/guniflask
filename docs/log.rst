.. _log:

Logging
=======

Getting Logger
--------------

guniflask将Flask的 ``app.logger`` 以及 ``foo`` 的logger 绑定到了gunicorn的 ``gunicorn.error`` 上。
因此可以在获取了Flask的 ``app`` 对象后使用 ``app.logger`` 纪录日志。
也可以在项目模块中按如下方式获取logger:

.. code-block:: python

    import logging

    log = logging.getLogger(__name__)

    log.info('Print log ...')


Log Level
---------

设置日志的级别需要通过添加gunicorn配置项 ``loglevel`` ，例如:

.. code-block:: python

    loglevel = 'warning'

日志级别包括:

- debug
- info
- warning
- error
- critical

gunicorn的配置项如何添加到项目中可参考 :ref:`config` 。

日志相关的配置项可参考gunicorn文档: http://docs.gunicorn.org/en/stable/settings.html#logging 。
