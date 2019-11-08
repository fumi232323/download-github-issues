import argparse
import logging
import re
from collections import defaultdict
from pathlib import PurePath
from typing import List, Dict, Tuple, Any

import requests

import settings
import templates

logger = logging.getLogger(__name__)


# GitHub list issues for a repository endpoint
# see: https://developer.github.com/v3/issues/#list-issues-for-a-repository
ISSUE_URL = 'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
IMAGE_URL_REGEX = r"!\[.*?\]\((https://user-images.githubusercontent.com/[\w\-\./]+)\)"
ATTACHMENTS_URL_REGEX = r"\[.*?\]\((https://github.com/{repo_owner}/{repo_name}/files/[\w\-\./]+)\)"
attachments_regex = ""

# File name to output issue
OUTPUT_FILENAME = '{issue_number}_{issue_title}.md'


def download(
        target_url: str, params: Dict[str, str] = None
) -> requests.models.Response:
    res = requests.get(
        target_url,
        params=params,
        auth=(settings.GITHUB_USER, settings.GITHUB_PASSWORD)
    )
    res.raise_for_status()

    return res


def generate_filename(issue: Dict[str, Any]) -> str:
    return OUTPUT_FILENAME.format(
        issue_number=issue['number'],
        issue_title=issue['title'].strip().replace('/', '-'),
    )


def format_comments(comments: List[Dict[str, Any]]) -> Tuple[str, Dict[str, List[str]]]:
    formatted = ""
    contents_urls = defaultdict()

    for comment in comments:
        formatted += templates.COMMENT.format(
            user=comment['user']['login'],
            created_at=comment['created_at'],
            html_url=comment['html_url'],
            body=comment['body'],
        )
        comment_id = f"{PurePath(comment['issue_url']).name}_{comment['id']}"
        contents_urls[comment_id] = collect_content_urls(comment['body'])

    return formatted, contents_urls


def format_issue(issue: Dict[str, Any], comments: str) -> str:
    return templates.ISSUE.format(
            number=issue['number'],
            title=issue['title'],
            html_url=issue['html_url'],
            state=issue['state'],
            created_at=issue['created_at'],
            author=issue['user']['login'],
            closed_at=issue['closed_at'] or '-',
            body=issue['body'],
            comments=comments,
        )


def collect_content_urls(string: str) -> List[str]:
    image_urls = re.findall(IMAGE_URL_REGEX, string)  # type: List[str]
    attachment_urls = re.findall(attachments_regex, string)  # type: List[str]

    return image_urls + attachment_urls


def serialize(issues: List[Dict[str, Any]]) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """
    API から取得した Issues and Comments をファイル出力用にフォーマットし、
    また、Issues や Comments に添付されているコンテンツの URL を収集して返す。

    :param issues: ひとつの Issue を表す辞書のリスト
    :return: 以下を保持する2カラムのタプル

      #. ファイル名を key に、Markdown 形式にフォーマットされた Issue と
         そのIssue に紐づく Comments のテキストをvalue に持つ辞書
      #. Issue number もしくは {Issue number}_{Comment id} をキーに、
         その Issue もしくは Comment に紐づくコンテンツの URL を value に持つ辞書
    """
    serialized = defaultdict()
    contents_urls = defaultdict()

    for issue in issues:
        if issue.get('pull_request'):
            # see: https://developer.github.com/v3/issues/#list-issues-for-a-repository
            # `List issues for a repository` API の返却値には Issue と PR の両方が含まれるため、ここで PR を除外する
            logger.info("Skipped #%s, because it is pull request.", issue['number'])
            continue

        logger.info("Downloading issue #%s", issue['number'])

        res = download(issue['comments_url'])
        comments, cont_urls = format_comments(res.json())

        serialized[generate_filename(issue)] = format_issue(issue, comments)

        contents_urls[str(issue['number'])] = collect_content_urls(issue['body'])
        contents_urls.update(cont_urls)

    return serialized, contents_urls


def output(issues: Dict[str, str]):
    settings.ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    for filename, issue in issues.items():
        with open(settings.ISSUES_DIR / filename, 'w', encoding="utf-8") as f:
            f.write(issue)

    logger.debug("%s issues were downloaded.", len(issues))


def download_contents(content_urls: Dict[str, List[str]]):
    count = 0
    for content_id, urls in content_urls.items():
        for url in urls:
            logger.info("Downloading contents of issue #%s", content_id)
            filepath = settings.CONTENTS_DIR / content_id / PurePath(url).name
            if filepath.exists():
                # Do not download if already downloaded.
                continue

            try:
                res = download(url)
                import time
                time.sleep(5)  # 待たないとfailするので
            except requests.exceptions.HTTPError:
                logger.warning("Failed downloading content. url: '%s'.", url, exc_info=True)
                continue

            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(res.content)
                count += 1

    logger.debug("%s contents were downloaded.", count)


def get_next_url(res: requests.models.Response) -> str:
    if res.links.get('next'):
        return res.links['next']['url']

    return ""


def main(repo_owner: str, repo_name: str, state: str, contents: bool):
    logger.info(
        "Start downloading issues. repo_owner: '%s', repo_name: '%s', state: '%s', contents: '%s'.",
        repo_owner, repo_name, state, contents
    )

    issue_url = ISSUE_URL.format(repo_owner=repo_owner, repo_name=repo_name)
    params = {'state': state}

    # TODO: ここどうなんだろう... `global` 使っているの、今まで見たことない....
    global attachments_regex
    attachments_regex = ATTACHMENTS_URL_REGEX.format(repo_owner=repo_owner, repo_name=repo_name)

    total = 0
    while issue_url:
        res = download(issue_url, params)
        issues, content_urls = serialize(res.json())
        output(issues)
        if contents:
            download_contents(content_urls)
        issue_url = get_next_url(res)
        total += len(issues)

    logger.info("Completed downloading issues. %s issues have been downloaded.", total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='You can download GitHub issues for a repository including comments at once '
                    'and output to markdown files.',
    )

    parser.add_argument(
        'repo_owner',
        type=str,
        help='You need to specify the owner of the repository.'
    )
    parser.add_argument(
        'repo_name',
        type=str,
        help='You need to specify the name of the repository.'
    )
    parser.add_argument(
        '-s', '--state',
        type=str,
        default='open',
        choices=['open', 'closed', 'all'],
        help='You can also specify the state of the issue if you like. The default is open.'
    )
    parser.add_argument(
        '-c', '--contents',
        action='store_true',
        help="Specify this option if you also need to download images and attachments."
    )

    args = parser.parse_args()
    logger.debug("args: '%s'", args)

    main(
        repo_owner=args.repo_owner,
        repo_name=args.repo_name,
        state=args.state,
        contents=args.contents,
    )
