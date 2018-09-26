.. _changelog:

Change log
==========

0.3.0 (2018-??-??)
------------------

- 在已有项目中使用guniflask init时会自动根据已有的配置推荐默认的项目名和端口号
- bin/manage.py添加了默认环境变量的设置
- 添加gunicorn默认配置 ``preload_app=True`` ，debug模式下自动设置 ``preload_app=False``
- 在 ``manage debug/start`` 命令中通过 ``-p`` 选项设置 ``active_profiles``
- ``manage initdb`` 会自动加载foo模块及子模块中所有声明的 ``db.Model``

0.2.5 (2018-09-18)
------------------

- table2model添加 ``server_default``
- ``to_dict`` , ``from_dict`` , ``update_by_dict`` 添加 ``ignore`` 参数，表示忽略哪些字段，如 ``ignore=['id', 'created_time']`` , ``ignore='id,created_time'`` 均表示忽略 ``id`` 和 ``created_time`` 字段
- ``from_dict`` 能够自动将 ``int`` 型的时间戳或GMT格式的时间戳转换为 ``datetime``

0.2.4 (2018-09-16)
------------------

- 修复钩子函数 ``init_app`` 没有被调用的bug
- ``config.settings`` 设定为app启动之后访问配置的途径，在启动app之前使用 ``config.settings`` 会raise RuntimeError
- 创建时间和更新时间字段改为存储本地时间戳，在调用model的 ``to_dict`` 方法时自动对没有设置时区的 ``datetime`` 字段填充本地时区
- many-to-one relationship默认添加 ``cascade='all, delete-orphan'``

0.2.3 (2018-09-14)
------------------

- ``db.Model`` 提供 ``update_by_dict`` 方法
- 对于符合 ``^create[d]?_(time|at)$`` 模式的 ``datetime`` 字段，视为创建时间字段，自动添加 ``default``
- 对于符合 ``^update[d]?_(time|at)$`` 模式的 ``datetime`` 字段，视为更新时间字段，自动添加 ``default`` 和 ``onupdate``
- 修复table2model生成relation的命名问题

0.2.2 (2018-09-13)
------------------

- 自动注册foo模块及子模块中所有声明的 ``Blueprint``
- 添加配置项 ``table2model_dest`` ，用于指定table2model生成结果的存放路径
- debug模式默认创建pid文件
- 修复 ``config.settings`` 获取配置出错的bug
- 修复 ``db.Model.from_dict``
- 修复生成项目的 ``tests`` 文件夹的路径
- Python>=3.5

0.2.1 (2018-09-12)
------------------

- 修复初始化项目时创建 __pycache__ 的bug
- 优化table2model导出的column type，修复部分已知bug
- 修复未创建日志目录和pid目录时不能start项目的bug

0.2.0 (2018-09-12)
------------------

- 新增根据数据库表自动生成 models 的功能
- 提供函数支持model和 ``dict`` 之间的转换
- 添加钩子函数 ``init_app(app, settings)``
- 将控制项目的各项命令整合到 bin/manage 中
- 通过 ``config.settings`` 获取配置
- foo.model.py -> foo/models
- db对象通过 ``from foo import db`` 导入

0.1.1 (2018-09-12)
------------------

- 修复模版中的错误

0.1.0 (2018-09-10)
------------------

Hello World!
