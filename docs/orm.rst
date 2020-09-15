.. include:: <isoamsa.txt>

.. _database_orm:

Database & ORM
==============

Database Access
---------------

项目默认基于Flask-SQLAlchemy实现对数据库的访问，生成项目文件 foo/app.py 中包含了 ``SQLAlchemy`` 对象的初始化方式，在项目其他位置可以通过如下方式获取该对象:

.. code-block:: python

    from foo import db

由于默认 conf/foo.py 中大写配置会自动注入到Flask的config中，因此我们可以在 conf/foo.py 中对数据库进行详细配置，具体的配置项可参考Flask-SQLAlchemy文档: http://flask-sqlalchemy.pocoo.org/config/ 。

Table to Model
--------------

在设计好数据库表之后，通过运行如下命令自动在 ``foo.models`` 模块中生成数据库表对应的model:

.. code-block:: bash

    $ bash bin/manage table2model

我们可以通过修改 :ref:`table2model_dest` 配置更改model存储的路径。

Model |xhArr|  dict
-------------------

我们对 ``db.Model`` 注入了两个成员函数:

- ``from_dict(dict_obj)`` : classmethod，将 ``dict`` 数据转为 ``db.Model`` 。
- ``to_dict()`` : method, 将 ``db.Model`` 转变为 ``dict`` 。
