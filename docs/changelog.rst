.. _changelog:

Changelog
=========

0.7.0 (2020-04-08)
------------------

- 将CLI相关功能分离到单独的项目guniflask-cli
- 依赖注入支持list和dict形式
- 添加@autowired，用于自动执行需要依赖注入的函数
- 扩展Flask响应请求的函数的参数，支持声明URL中的查询参数、body中的json对象
- 对于guniflask的内置扩展功能提供更为统一的配置方式
- 减少了initdb和table2model命令的参数，model所在路径的修改、多数据库相关配置等统一在 ``table2model_dest`` 中设置
- 为避免歧义，@roles_required修改为@has_any_role，@authorities_required修改为@has_any_authority，同时提供@has_role和@has_authority
- JwtManager创建access token时用户自定义字段会作为User的属性
- init命令将生成 foo/config 的目录，用于存放应用的配置
- @global_singleton改为app级别的单例模式，当gunicorn启动多个worker时，只有一个worker下的单例会生效

0.6.1 (2020-03-15)
------------------

- 修复@async_run修饰带参数方法时的bug
- 修复调用@async_run修饰的方法时的requst context

0.6.0 (2020-03-13)
------------------

- 提供实例的上下文管理功能，支持基于类型、名称的依赖注入
- 支持异步运行、定时任务
- initdb和table2model命令添加bind参数，以支持多数据库配置
- 移除BgProcess功能
- JwtManager创建access token的接口发生改变
- 移除对gunicorn的默认配置 ``preload_app=True``
- 移除apidoc
- Python>=3.6

0.5.1 (2019-12-23)
------------------

- ``@blueprint`` 支持无括号形式
- fix: 避免重复注册Blueprint
- 项目初始化添加不使用认证方案的选项

0.5.0 (2019-12-18)
------------------

- initdb命令提供设定profile的选项，默认为 ``dev``
- table2model支持配置不同的tables生成的models放到不同的模块中
- 添加 ``jwt`` 配置项控制是否启用内置的基于JWT的认证方案
- 支持基于装饰器生成Blueprint
- 调整部分内置Flask插件的加载形式

0.4.3 (2019-09-11)
------------------

- table2model命令提供设定profile的选项，默认为 ``dev``
- table2model不再加载项目模块，避免因项目错误导致不能正常生成model
- BgProcess捕获运行时异常并记录在日志中
- model添加 ``result_to_dict`` 方法

0.4.2 (2019-08-20)
------------------

- fix: 在后台进程启动后再载入BgProcess所在模块，避免因为过早的import导致gevent报错
- ``to_dict`` , ``from_dict`` , ``update_by_dict`` 添加 ``only`` 和 ``only_not_none`` 参数

0.4.1 (2019-08-13)
------------------

- 添加对后台进程(BgProcess)的支持

0.4.0 (2019-07-25)
------------------

- 简化 foo/app.py 中的代码，便于后续新特性在更新guniflask之后即可使用，无需再关注 app.py 代码的变化
- 移除 foo/hooks.py ，原有代码并入 foo/app.py 中
- 移除 bin/manage.py ，原有代码并入guniflask中
- 环境变量配置 ``VIRTUAL_ENV`` 更名为 ``GUNIFLASK_VIRTUAL_ENV``
- 修复 ``server_default`` 的自动生成
- debug添加后台运行模式
- start支持关闭后台运行模式
- 添加docker相关配置文件
- 支持根据注释自动生成API文档

0.3.1 (2018-10-31)
------------------

- 修复生成的JWT token的类型: ``bytes`` -> ``str``

0.3.0 (2018-10-24)
------------------

- ``guniflask init`` 会将用户的选择保存在 .guniflask-init.json 中，再次使用该命令会直接使用保存的选择重新生成项目，如需重新进行选择可使用 ``guniflask init -f``
- bin/manage.py 添加了默认环境变量的设置
- 添加gunicorn默认配置 ``preload_app=True`` ，debug模式下自动设置 ``preload_app=False``
- ``active_profiles`` 改为只能通过环境变量进行设置
- 在 bin/manage debug|start 命令中可以通过 ``-p`` 选项设置 ``active_profiles`` 对应的环境变量
- ``manage initdb`` 会自动加载foo模块及子模块中所有声明的 ``db.Model``
- Flask app的name更正为项目的名称
- 脚本文件命名: conf/foo-env.sh -> conf/app-env.sh , bin/foo-config.sh -> bin/app-config.sh
- 提供 ``settings`` 对象获取配置
- 移除 conf/wsgi.py
- 提供基于JWT的用户权限认证方案
- 生成的依赖文件的位置: requirements.txt -> requirements/app.txt , requirements_test.txt -> requirements/test.txt
- bin/manage debug 默认添加名为 ``dev`` 的profile, bin/manage start 默认添加名为 ``prod`` 的profile

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
