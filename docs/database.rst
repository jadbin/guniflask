.. _database:

Database Access
===============

项目基于Flask-SQLAlchemy实现数据的访问。
我们可以通过如下方式获取 ``SQLAlchemy`` 对象 ``db`` :

.. code-block:: python

    from foo import db

Database Settings
-----------------

我们可以在 conf/foo.py 中对数据库进行配置，详细的配置项可参考Flask-SQLAlchemy文档: http://flask-sqlalchemy.pocoo.org/config/ 。

只要配置了 ``SQLALCHEMY_DATABASE_URI`` ，项目会在启动前自动调用 ``db.init_app(app)`` 。

Declaring Models
----------------

我们约定项目中使用的model在 ``foo.models`` 模块及其子模块中声明。
下面给出了一个定义model的示例。

.. code-block:: python

    from foo import db

    class Foo(db.Model):
        __tablename__ = 'foo'

        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        name = db.Column(db.String(32))

更多有关如何定义model的详细信息可参考Flask-SQLAlchemy文档: http://flask-sqlalchemy.pocoo.org/models/ 。

Initializing Database
---------------------

我们可以通过运行初始化数据库的命令自动生成 ``foo.models`` 中定义的model对应的数据库表:

.. code-block:: bash

    $ bash bin/manage initdb

如果需要覆盖已经创建的数据库表需要添加 ``-f`` 选项:

.. code-block:: bash

    $ bash bin/manage initdb -f
