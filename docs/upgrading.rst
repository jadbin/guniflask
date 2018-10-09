.. _upgrading:

Upgrade to New Releases
=======================

通过pip升级guniflask::

    $ pip install -U guniflask

之后需要在项目根目录下运行如下命令（重新生成项目）::

    $ guniflask init

重新生成项目时会覆盖部分已修改的文件，这时可以借助Git等版本管理工具选择保留正常的更新代码，并舍弃无用的覆盖（例如重新生成的配置文件）。

在guniflask升级过程中可能会带来非兼容性更新，我们接下来将提供升级到各个新版本的指南。

假设我们的项目名为foo。

Version 0.3
-----------

在新版本中，生成的配置文件将统一命名，不再和项目名相关。
bin/foo-config.sh 文件统一命名为 bin/app-config.sh ，删除 bin/foo-config.sh 即可。
conf/foo-env.sh 文件统一命名为 conf/app-env.sh ，将配置的环境变量移至新文件，之后删除 conf/foo-env.sh 。
conf/foo.py 文件统一命名为 conf/app.py ，将配置项移至新文件，之后删除 conf/foo.py 。

在新版本中，我们移除了 ``config`` 对象，改为直接通过 ``settings`` 对象获取配置项。
因此如果原项目中存在如下引入 ``config`` 对象的代码:

.. code-block:: python

    from foo import config

需要改为:

.. code-block:: python

    from foo import settings

原项目中使用 ``config.settings`` 的地方改为直接使用 ``settings``。
