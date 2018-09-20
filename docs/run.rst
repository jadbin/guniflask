.. _run:

Running guniflask
=================

guniflask用于自动化构建基于flask + gunicorn的服务端的基础代码。

创建项目目录，并在运行guniflask的初始化项目命令:

.. code-block:: bash

    $ mkdir foo && cd foo
    $ guniflask init

接下来会以对话的形式完成项目的初始配置，当选择默认设置时直接按Enter键即可。

.. code-block:: text

    ? (1/2) What is the base name of your application? (foo)

这里需要输入项目的名称，同时作为该项目的Python模块的名称，括号中给出的是根据项目根目录生成的默认名称。
项目名称可以包含数字、字母和下划线 ( _ ) ，不能以数字开头。

.. code-block:: text

    ? (2/2) Would you like to run your application on which port? (8000)

这里需要填写项目运行在哪个端口，默认为 ``8000`` 端口。

之后，会在项目根目录下生成项目的初始代码。

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

.. note::
    - 为了便于描述，在后续文档中我们用 ``foo`` 替代项目的实际名称。
    - 如果没有特殊声明，默认后续文档中执行命令的过程都是在项目根目录下完成的。
