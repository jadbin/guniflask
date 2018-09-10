.. _deploy:

Deploying Application
=====================

Active Profiles
---------------

如果采用多profile的形式管理配置文件，请确保在启动项目前已正确配置 ``active_profiles`` 。

Virtual Environment
-------------------

guniflask生成的项目支持配置Python标准库生成的虚拟环境。
我们可以通过修改 conf/${proj}-env.sh 中有关虚拟环境的配置项使得项目在虚拟环境下启动:

.. code-block:: bash

    # The home directory of virtual environment
    export VIRTUAL_ENV=${VIRTUAL_ENV}

环境变量的值为虚拟环境所在文件夹的根目录。

也可以通过其他方式在启动项目前设定好环境变量 ``VIRTUAL_ENV`` 。

Starting Application
--------------------

运行项目的启动脚本:

.. code-block:: bash

    $ bash bin/start-${proj}.sh

等待几秒后会看到项目成功启动的提示。

如果提示项目启动失败，可以根据控制台的提示信息以及项目的日志纪录排查出错原因。
项目的错误日志默认存放在 ``${home}/.log`` 文件夹中。

Stopping Application
--------------------

运行项目的停止脚本:

.. code-block:: bash

    $ bash bin/stop-${proj}.sh

等待几秒后会看到项目成功停止的提示。

如果提示不能成功停止项目，则可以尝试再次运行该脚本。
如果仍不能停止项目，则可以通过 ``kill -9`` 强制停止项目。
项目的pid默认存放在 ``${home}/.pid`` 文件夹中。
