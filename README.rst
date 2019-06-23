Download GitHub Issues
=======================
Download GitHub issues for a repository including comments at once and output to markdown files.

ある特定の GitHub repository の issues (comments も含む) を一括ダウンロードして、 Markdown 形式のファイルに出力します。


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
  # Open .env file and write your github account and password in .env file
  # .env ファイルを開き、あなたの GitHub アカウントとパスワードを記入してください


Usage
-----
The following command will download issues including comments from the specified GitHub repository and output them as Markdown format files under ``./issues`` directory.

以下のようにコマンドを実行すると、指定した GitHub リポジトリから issues (各 issue に紐づく comments も含む) をダウンロードして ``./issues`` 配下へ出力します。

.. code-block:: bash

  (venv) $ python download.py <repo_owner> <repo_name> [-s|--state <issue_state>]
