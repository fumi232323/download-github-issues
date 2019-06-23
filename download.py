import argparse
import logging
from typing import List, Dict, Any

import requests

import settings

logger = logging.getLogger(__name__)

# Template: Issue
ISSUE_TEMPLATE = '''# #{number} {title}

* issue_url: {html_url}
* state: {state}
* created_at: {author} opened this issue at {created_at}
* closed_at: {closed_at}

***
{author} commented at {created_at}
***
{body}

{comments}
'''

# Template: Comment
COMMENT_TEMPLATE = '''***
{user} commented at {created_at}
({html_url})
***

{body}

'''

# GitHub get issues point
GITHUB_ISSUE_URL = 'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
OUTPUT_DIR = settings.PROJECT_PATH / settings.ISSUES_PATH
# File name to output issue
OUTPUT_FILENAME = '{issue_number}_{issue_title}.md'


def download(
        target_url: str, params: Dict[str, str] = None
) -> List[Dict[str, Any]]:
    """

    :param target_url:
    :return:
    """
    r = requests.get(
        target_url,
        params=params,
        auth=(settings.GITHUB_USER, settings.GITHUB_PASSWORD)
    )
    r.raise_for_status()

    return r.json()


def generate_filename(issue: Dict[str, Any]) -> str:
    """

    :param issue:
    :return:
    """
    return OUTPUT_FILENAME.format(
        issue_number=issue['number'],
        issue_title=issue['title'].strip().replace('/', '-'),
    )


def generate_formatted_comments(url: str) -> str:
    """

    :param url:
    :return:
    """
    comments = ""
    for comment in download(url):
        comments += COMMENT_TEMPLATE.format(
            user=comment['user']['login'],
            created_at=comment['created_at'],
            html_url=comment['html_url'],
            body=comment['body'],
        )

    return comments


def generate_formatted_issue(url: str, params: Dict[str, str] = None) -> str:
    """

    :param url:
    :param params:
    :return:
    """
    for issue in download(url, params):
        text = ISSUE_TEMPLATE.format(
            number=issue['number'],
            title=issue['title'],
            html_url=issue['html_url'],
            state=issue['state'],
            created_at=issue['created_at'],
            author=issue['user']['login'],
            closed_at=issue['closed_at'] or '-',
            body=issue['body'],
            comments=generate_formatted_comments(issue['comments_url']),
        )
        filename = OUTPUT_FILENAME.format(
            issue_number=issue['number'],
            issue_title=issue['title'].strip().replace('/', '-'),
        )
        yield text, filename


def main(repo_owner: str, repo_name: str, state: str):
    """
    TODO:
        * 画像を取って来たい
        * README を書く
        * template をどうにかしたいような...
        * DocString 書く
    """
    issue_url = GITHUB_ISSUE_URL.format(
        repo_owner=repo_owner,
        repo_name=repo_name,
    )
    params = {'state': state}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for text, filename in generate_formatted_issue(issue_url, params):
        with open(OUTPUT_DIR / filename, 'w', encoding="utf-8") as f:
            f.write(text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='You can download Github issues including comments at once and output to markdown files.',
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
        default='all',
        choices=['open', 'closed', 'all'],
        help='You can also specify the state of the issue if you like.'
    )

    args = parser.parse_args()
    logger.debug("args: '%s'", args)

    main(
        repo_owner=args.repo_owner,
        repo_name=args.repo_name,
        state=args.state,
    )
