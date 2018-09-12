.. _blueprints:

Blueprints
==========

Blueprint Concept
-----------------

Flask提供了blueprint的概念用于模块化构建服务端代码，详细文档可参考Flask文档: http://flask.pocoo.org/docs/blueprints/ 。

Declaring Blueprints
--------------------

项目用到的blueprint可以在 ``foo`` 模块任意位置进行声明，项目启动时会自动将所有声明的 ``Blueprint`` 自动注册到Flask app中。

``foo.blueprints.hello_world`` 模块提供了一个简单的使用blueprint的示例。
