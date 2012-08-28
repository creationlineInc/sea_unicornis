===============
 Sea Unicornis
===============

Sea Unicornis は `kotti_mapreduce`_ を利用する `Kotti`_ アドオンとして開発されています。

.. _kotti_mapreduce: http://pypi.python.org/pypi/kotti_mapreduce/
.. _Kotti: http://pypi.python.org/pypi/Kotti

インストール方法
================

github からソースをクローンします::

    $ git clone git@github.com:creationlineInc/sea_unicornis.git
    $ cd sea_unicornis
    $ python setup.py develop

Python パッケージとして PyPI に公開すれば pip コマンドでもインストールできます::

    $ pip install sea_unicornis

設定
====

Kotti サイトで sea_unicornis アドオンを有効にするには、ini ファイルに次のように設定します::

    kotti.configurators =
        kotti_mapreduce.kotti_configure
        sea_unicornis.kotti_configure

ドキュメント
============

Sea Unicornis のドキュメントについては https://github.com/creationlineInc/sea_unicornis/wiki を参照してください。
