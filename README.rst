Download GitHub Issues
=======================
Download issues (including comments attached to each issue) from the specified GitHub repository and output them as Markdown format files.

指定した GitHub repository から issues (各 issue に紐づく comments も含む) をダウンロードして、 Markdown 形式のファイルに出力します。

Requirements
-------------
:Python: 3.6 or later.


Setup
-----

.. code-block:: bash

  $ cd ~
  $ git clone git@github.com:fumi232323/download-github-issues.git
  $ git checkout master
  $ python3 -m venv ~/venv
  $ source ~/venv/bin/activate
  (venv) $ cd ~/download-github-issues
  (venv) $ pip install -r requirements.txt
  $ mv example.env .env
  # Open the .env file and enter your GitHub account and password.
  # .env ファイルを開き、あなたの GitHub アカウントとパスワードを記入してください


Usage
-----

.. code-block:: bash

  (venv) $ python download.py <repo_owner> <repo_name> [-s|--state <issue_state>] [-c|--contents]


Description
^^^^^^^^^^^^
This command will download issues including comments from the specified GitHub repository and output them as Markdown format files under ``./issues`` directory.

コマンドを実行すると、指定した GitHub リポジトリから issues (各 issue に紐づく comments も含む) をダウンロードして ``./issues`` 配下へ出力します。


Options
^^^^^^^^

:-s|--state <issue_state>: You can also specify the state of the issue if you like. You can choose from 'open', 'closed' and 'all'. The default is open.
:-c|--contents: Specify this option if you also need to download images and attachments. Then output to ``. / Issues / images``.

