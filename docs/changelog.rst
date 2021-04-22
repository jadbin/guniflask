.. _changelog:

Changelog
=========

0.12.5 (2021-04-22)
-------------------

- 默认使用 ``GeventScheduler``

0.12.4 (2021-04-19)
-------------------

- 添加健康检查接口 ``GET /health``

0.12.3 (2021-04-15)
-------------------

- 对时间类型的参数的格式化改由pydantic内置的函数实现

0.12.2 (2021-04-09)
-------------------

- 修复current_user的递归调用错误

0.12.1 (2021-04-08)
-------------------

- 修复stop命令

0.12.0 (2021-04-08)
-------------------

- 移除服务发现功能，改由k8s支持

0.11.15 (2021-03-30)
--------------------

- 非后台运行状态下，默认日志输出到控制台

0.11.14 (2021-03-24)
--------------------

- 修复bean加载过程中可能会访问 ``@blueprint`` 中定义的 ``@property`` 的问题

0.11.13 (2021-03-12)
--------------------

- 添加 ``head_route`` 装饰器

0.11.12 (2021-03-04)
--------------------

- 修复在未定义 ``config_key`` 时Consul拉取应用配置的错误

0.11.11 (2021-03-04)
--------------------

- 配置文件支持yaml、json格式
- 支持从Consul拉取应用配置，同时会覆盖本地已有的配置
- 移除 ``app_id`` 配置项，健康检查接口改为核对应用名称

0.11.10 (2021-02-01)
--------------------

- 集成pydantic，DataModel继承pydantic的BaseModel
- 项目模版生成 ``__version__`` ，用于标识应用版本

0.11.9 (2021-01-25)
-------------------

- 修复自动映射数据类型时对None值的处理

0.11.8 (2021-01-22)
-------------------

- 修复由build引起的无法识别builtin参数类型的问题

0.11.7 (2021-01-18)
-------------------

- 修复setup.py中的依赖信息

0.11.6 (2021-01-18)
-------------------

- 修复未指定算法时JwtManager可能无法正常解码token的问题
- 新增build命令，将项目py文件编译为so文件

0.11.5 (2021-01-11)
-------------------

- 自动推断项目名称时支持项目名包含大写字母
- 修复部分情况下table2model生成的代码缺少引入依赖的问题
- table2model支持在不加载app的前提下仅依赖于配置文件实现数据模型的生成
- 新增 ``app_id`` 配置项，默认填充为应用指定的唯一标识
- 新增 ``ip_address`` 配置项，默认填充获取的本机IP地址，用于服务注册等功能

0.11.4 (2020-11-18)
-------------------

- BaseModelMixin: ``to_dict`` 不再默认递归映射relationship，通过 ``include`` 参数指定处理哪些relationship
- table2model: 优化了判断one-to-one关系的方法; 在定义one-to-one和one-to-many关系时用 ``back_populates`` 取代 ``backref``

0.11.3 (2020-11-12)
-------------------

- 提供以对象形式存储数据的基类 ``DataModel``
- 去掉生成的py文件中的encoding注释

0.11.2 (2020-11-07)
-------------------

- BaseModelMixin: ``from_dict`` 、 ``to_dict`` 、 ``update_by_dict`` 支持递归， ``update_by_dict`` 暂时不支持更新list形式的字段
- 修复jwt配置模版中抽取authorization header的bug

0.11.1 (2020-11-05)
-------------------

- 支持构建测试应用时自动推断项目的根目录

0.11.0 (2020-11-05)
-------------------

- 项目依赖默认不再生成PyMySQL，用户可根据实际使用的数据库选择合适的依赖
- BaseModelMixin声明query的类型
- 提供接口级别单元测试方案
- 移除oauth2相关功能，后续身份认证、授权等相关功能将基于Keycloak实现
- ``current_user`` 的定义移动到 ``guniflask.security`` 模块中
- 内置配置项 ``project_name`` 更名为 ``app_name`` ，环境变量配置项 ``GUNIFLASK_PROJECT_NAME`` 更名为 ``GUNIFLASK_APP_NAME``

0.10.0 (2020-10-19)
-------------------

- manage现在可以在任何路径下运行
- debug模式下会融合对 ``reload_extra_files`` 的默认配置和自定义配置
- gunicorn配置恢复默认使用gevent worker
- 暂时移除对ASGI的相关支持，包括websocket
- 修复 ``from guniflask.config import Settings`` 的引用错误

0.9.2 (2020-09-17)
------------------

- 新增 ``guniflask_cli.workers.UvicornWorker`` 解决uvicorn提供的worker中存在的问题：(1) debug模式下worker无法reload；(2) 父进程退出后worker没有退出

0.9.1 (2020-09-16)
------------------

- 修复未加载gunicorn配置的错误

0.9.0 (2020-09-16)
------------------

- 提供基于类型和默认值为视图函数注入request参数（query、body、file、form、header、cookie）的机制
- 通过.env文件设置环境变量，移除原有和环境变量配置相关的shell文件
- 新增 ``@condition_on_setting`` ，基于配置项是否存在控制是否初始化实例
- 移除initdb命令
- table2model取消了只支持MySQL的限制
- gunicorn worker默认使用 ``uvicorn.workers.UvicornWorker``
- 支持websocket

0.8.9 (2020-08-20)
------------------

- 非daemon模式默认不再生成PID文件（修复bug）

0.8.8 (2020-08-18)
------------------

- 移除 ``GUNIFLASK_ID_STRING``
- 非daemon模式默认不再生成PID文件

0.8.7 (2020-08-11)
------------------

- 修复服务发现功能

0.8.6 (2020-08-10)
------------------

- health endpoint添加了对project name的校验

0.8.5 (2020-08-10)
------------------

- 修复服务注册时找不到app context的问题
- 移除settings添加内置变量 ``id_string`` ，环境变量 ``GUNIFLASK_ID_STRING`` 只在服务外部环境中发挥作用

0.8.4 (2020-08-09)
------------------

- stop和restart命令支持设置active profiles，用于处理在profile后缀的gunicorn配置文件中设置了 ``pidfile`` 的情况
- 修复了由自动加载服务发现配置可能导致的循环引用问题

0.8.3 (2020-08-07)
------------------

- settings添加内置变量 ``id_string`` ，对应环境变量 ``GUNIFLASK_ID_STRING``
- health endpoint添加了active profiles的校验，避免程序在错误的profile下启动后无法从Consul中删除服务

0.8.2 (2020-08-04)
------------------

- 多个profile中通过dict作出的配置在读取时应当进行合并，而不是简单替换

0.8.1 (2020-08-04)
------------------

- 添加了服务发现和负载均衡功能，支持通过服务名定位到服务实例
- MasterLevelLock更名为ServiceLock，通过项目名称和端口号区别实例，解除对gunicorn的依赖
- 配置guniflask.cors之后自动进行跨域配置

0.8.0 (2020-08-01)
------------------

- guniflask-cli和guniflask的版本同步
- 对 ``SQLALCHEMY_TRACK_MODIFICATIONS`` 的默认配置改由guniflask-cli直接生成到项目代码中
- 默认添加gunicorn配置项 ``proc_name`` 为项目名称，便于查看进程信息
- 项目配置文件的读取改由guniflask-cli完成
- 移除@global_singleton，相关功能可以通过MasterLevelLock实现
- guniflask-manage中的指令合并到guniflask中
- init命令生成项目时移除了选择应用类型的步骤
- 默认生成开启跨域的配置
- 支持将服务注册到Consul
