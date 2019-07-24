.. _upgrading:

Upgrading to New Releases
=========================

通过pip升级guniflask::

    $ pip install -U guniflask

之后需要在项目根目录下运行如下命令（重新生成项目）::

    $ guniflask init

重新生成项目时会覆盖部分已修改的文件，这时可以借助Git等版本管理工具选择保留正常的更新代码，并舍弃无用的覆盖（例如重新生成的配置文件）。

在guniflask升级过程中可能会带来非兼容性更新，我们接下来将提供升级到各个新版本的指南。

.. note::

    假设我们的项目名为foo。

Version 0.4
-----------

对 foo/app.py 中的代码进行了重新组织，保留对象的定义并移除了原有的功能函数。
foo/hooks.py 中的代码追加到 foo/app.py 后删除 foo/hooks.py 。
移除 ``app_default_settings`` 对象，相关配置通过 ``make_settings`` 进行设置。

删除 bin/manage.py 。

删除 tests 目录下项目自动生成的测试文件。

Version 0.3
-----------

bin/foo-config.sh 文件统一命名为 bin/app-config.sh ，删除 bin/foo-config.sh 即可。
conf/foo-env.sh 文件统一命名为 conf/app-env.sh ，将配置的环境变量移至新文件，之后删除 conf/foo-env.sh 。
删除 conf/wsgi.py 。

依赖文件 requirements.txt 移至 requirements/app.txt ， requirements_test.txt 移至 requirements/test.txt 。

现在在 conf/foo.py 中设置 ``active_profiles`` 无效，需要在 bin/manage debug|start 命令中通过 ``-p`` 选项设置 ``active_profiles`` 。
bin/manage debug 默认添加名为 ``dev`` 的profile, bin/manage start 默认添加名为 ``prod`` 的profile。
