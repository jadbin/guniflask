.. _blueprints:

Blueprints
==========

Blueprint Concept
-----------------

Flask提供了blueprint的概念用于模块化构建服务端代码，详细文档可参考Flask文档: http://flask.pocoo.org/docs/blueprints/ 。

Declaring Blueprints
--------------------

我们约定项目中的blueprint在 ``${proj}.blueprints`` 模块及其子模块中声明， ``${proj}.blueprints.hello_world`` 模块提供了一个简单的使用blueprint的示例。

Auto Registering
----------------

在项目启动时会自动将 ``${proj}.blueprints`` 模块及其子模块中声明的 ``Blueprint`` 自动注册到Flask app中。
