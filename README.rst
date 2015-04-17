说明
====


环境要求
--------

* 平台: ``*nix``
* 开发语言: ``python2.7.x``


Python扩展
----------

* ``pyyaml``
* ``simplejson``
* ``sqlite3`` (2.5.x以上内置 编译python时注意有没有找到所需的sqlite3开发包，否则找不到sqlite3模块)

.. code-block:: python

   >>> pip install pyyaml
   >>> pip install simplejson


运行
----

* 拷贝config.inc.py到config.py 根据实际情况修改配置文件。

.. code-block:: python

   >>> cp config.inc.py config.py

* 如果服务器信息是基于文件配置的(加载路径: ``config.SERVER_DIR``)，首次运行或者文件配置有更新，执行下面的命令将服务器信息加载到数据库中，否则跳过这一步。

.. code-block:: python

   >>> make reload
   或者
   >>> python sso.py -s -r

* 启动

.. code-block:: python

   >>> make
   或者
   >>> python sso.py -s

* 更多参数及用法:

.. code-block:: python

   >>> python sso.py --help


数据结构
--------

参见 :class:`schema.Schema`


添加数据源
----------

目前内置的数据源是基于文件配置和sqlite数据库的。

如果想要支持其他类型的数据源，修改配置文件中的 :data:`ENGINE` 项，并在adapter目录下添加对应名称的模块和对应规则的类，类须继承自 :class:`apdater.base.BaseAdapter` 并实现其定义的抽象方法。

例如: 如果定义 `ENGINE = 'mongodb'`，那么需要在adapter目录下添加mongodb.py文件，并在mongodb.py中定义MongodbAdapter类。

具体请参考 :module:`adapter.sqlite`。
