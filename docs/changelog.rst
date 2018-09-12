.. _changelog:

Change log
==========

0.2.2 (2018-09-13)
------------------

- 自动注册foo模块及自模块中所有声明的 ``Blueprint``
- 添加配置项 ``table2model_dest`` ，用于指定table2model生成结果的存放路径
- debug模式默认创建pid文件
- 修复 ``config.settings`` 获取配置出错的bug
- 修复 ``db.Model.from_dict``

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
