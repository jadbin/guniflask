.. _deploy:

Deploying Application
=====================

Active Profiles
---------------

如果采用多profile的形式管理配置文件，请确保在启动项目前已正确配置 ``active_profiles`` 。

Starting Application
--------------------

运行如下命令启动项目:

.. code-block:: bash

    $ bash bin/manage start

如果提示项目启动失败，可以根据控制台的提示信息以及项目的日志纪录排查出错原因。
项目的错误日志默认存放在项目根目录下 .log 文件夹中。

Stopping Application
--------------------

运行如下命令停止项目:

.. code-block:: bash

    $ bash bin/manage stop

项目的pid默认存放在项目根目录下 .pid 文件夹中。
