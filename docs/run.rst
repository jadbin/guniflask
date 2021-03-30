.. _run:

Running guniflask
=================

首先安装guniflask项目生成工具guniflask-cli用于自动化构建项目的基础代码::

    $ pip install -U guniflask-cli

创建项目目录，并运行guniflask的初始化项目命令:

.. code-block:: bash

    $ mkdir <proj> && cd <proj>
    $ guniflask init

其中 <proj> 表示项目名称。
接下来会以对话的形式完成项目的初始配置，当选择默认设置时直接按Enter键即可。

根据导引完成配置之后，会在项目根目录下生成项目的初始代码。

如果生成和文件和原文件产生了冲突，则会有如下提示:

.. code-block:: text

    ? Overwrite some_file_here? (Y/n/a/x)

这里可以输入如下指令:

- ``y`` : 覆盖该文件 (默认选项)
- ``n`` : 跳过该文件
- ``a`` : 覆盖该文件以及所有后续冲突的文件
- ``x`` : 中止操作

最后，生成完所有项目文件后会提示项目创建成功。

.. warning::
    建议在运行guniflask前使用Git等版本控制工具保存当前项目的所有更改，以免在生成项目文件的过程中替换了未保存的更改。
