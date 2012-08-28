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

実行方法 (開発環境)
===================

開発環境向けの `development.ini` を使って以下のように実行します。
`--reload` オプションを付けることでプログラム変更時に自動的にサーバーが再起動されます。
初回起動時、カレントディレクトリに `Kotti.db` (SQLite) が作成されます::

    $ pserve development.ini --reload
    Starting subprocess with file monitor
    Sea Unicornis site is initialized
    Starting server in PID 1583.
    serving on http://0.0.0.0:6543

.. note::

   `development.ini` はデバッグ向け設定のため、本番環境では新たに ini ファイルを作成します。

ドキュメント
============

Sea Unicornis のドキュメントについては https://github.com/creationlineInc/sea_unicornis/wiki を参照してください。
