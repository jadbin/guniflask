.. _blueprints:

Blueprints
==========

Blueprint Concept
-----------------

Flask提供了blueprint的概念用于模块化构建服务端代码，详细文档可参考Flask文档: http://flask.pocoo.org/docs/blueprints/ 。

Declaring Blueprint
-------------------

项目用到的 ``Blueprint`` 可以在任意位置进行声明，项目启动时会自动将所有声明的 ``Blueprint`` 自动注册到Flask app中。

Using @blueprint
----------------

我们可以使用装饰器来替代显示的声明 ``Blueprint`` 。
下面的代码给出了一个运算加法的接口的示例。

.. code-block:: python

    from flask import request

    from guniflask.web import blueprint, post_route


    @blueprint('/api')
    class MathController:
        def __init__(self):
            self.add_service = lambda a, b: a + b

        @post_route('/add')
        def add(self):
            data = request.json
            return {'result': self.add_service(data.get('a'), data.get('b'))}
