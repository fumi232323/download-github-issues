import argparse
import logging
from typing import List, Dict, Tuple, Any

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

# GitHub list issues for a repository endpoint
# see: https://developer.github.com/v3/issues/#list-issues-for-a-repository
GITHUB_ISSUE_URL = 'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
# directory name to output issues
OUTPUT_DIR = settings.PROJECT_PATH / settings.ISSUES_PATH
# File name to output issue
OUTPUT_FILENAME = '{issue_number}_{issue_title}.md'


def download(
        target_url: str, params: Dict[str, str] = None
) -> requests.models.Response:
    r = requests.get(
        target_url,
        params=params,
        auth=(settings.GITHUB_USER, settings.GITHUB_PASSWORD)
    )
    r.raise_for_status()

    return r


def generate_filename(issue: Dict[str, Any]) -> str:
    return OUTPUT_FILENAME.format(
        issue_number=issue['number'],
        issue_title=issue['title'].strip().replace('/', '-'),
    )


def generate_formatted_comments(comments: List[Dict[str, Any]]) -> str:
    comments_text = ""
    for comment in comments:
        comments_text += COMMENT_TEMPLATE.format(
            user=comment['user']['login'],
            created_at=comment['created_at'],
            html_url=comment['html_url'],
            body=comment['body'],
        )

    return comments_text


def generate_formatted_issue(issue: Dict[str, Any]) -> str:
    return ISSUE_TEMPLATE.format(
            number=issue['number'],
            title=issue['title'],
            html_url=issue['html_url'],
            state=issue['state'],
            created_at=issue['created_at'],
            author=issue['user']['login'],
            closed_at=issue['closed_at'] or '-',
            body=issue['body'],
            comments=generate_formatted_comments(
                download(issue['comments_url']).json()
            ),
        )
def get_next_url(r: requests.models.Response) -> str:
    if r.links.get('next'):
        return r.links['next']['url']

    return ""


def fetch_issues(url: str, params: Dict[str, str] = None) -> Tuple[str, int]:
    r = download(url, params)
    count = 0

    for issue in r.json():
        if issue.get('pull_request'):
            logger.info("Skip pull request #%s.", issue['number'])
            continue

        logger.info("Downloading issue #%s.", issue['number'])

        text = generate_formatted_issue(issue)
        filename = generate_filename(issue)
        with open(OUTPUT_DIR / filename, 'w', encoding="utf-8") as f:
            f.write(text)

        count += 1

    return get_next_url(r), count


def main(repo_owner: str, repo_name: str, state: str):
    """
    TODO:
        * 画像を取って来たい
        * template をどうにかしたいような...
        * log をつける
    """
    logger.info("Start downloading Issues. repo_owner: '%s', repo_name: '%s', state: '%s'.", repo_owner, repo_name, state)

    issue_url = GITHUB_ISSUE_URL.format(repo_owner=repo_owner, repo_name=repo_name)
    params = {'state': state}
    total = 0
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    while issue_url:
        issue_url, fetched_count = fetch_issues(issue_url, params)
        total += fetched_count
        logger.info("%s issues were downloaded.", total)

    logger.info("Download of Issues complete. %s issues have been downloaded.", total)


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

    args = parser.parse_args()
    logger.debug("args: '%s'", args)

    main(
        repo_owner=args.repo_owner,
        repo_name=args.repo_name,
        state=args.state,
    )
