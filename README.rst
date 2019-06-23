Download GitHub issues
=======================
Download GitHub issues for a repository including comments at once and output to markdown files.
GitHub の ある特定の repository の issues (comments も含む) を一括ダウンロードして、 Markdown 形式のファイルに出力します。


Requirements
-------------
:Python: 3.6 or later.


Setup
-----

.. code-block:: bash

  $ cd ~
  $ git clone <リポジトリのURL>
  $ git checkout master
  $ python3 -m venv ~/venv
  $ source ~/venv/bin/activate
  (venv) $ cd ~/download-github-issues
  (venv) $ pip install -r requirements.txt
  $ mv example.env .env
  # Open .env file and write your github account and password in .env file
  # .env ファイルを開き、あなたの GitHub アカウントとパスワードを記入してください


Usage
-----

.. code-block:: bash

  (venv) $ python download.py <repo_owner> <repo_name> [-s|--state <state>]
