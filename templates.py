# Issue ##########
ISSUE = '''# #{number} {title}

* Issue url: {html_url}
* State: {state}
* Created at: {author} opened this issue at {created_at}
* Closed at: {closed_at}

***
{author} commented at {created_at}
***
{body}

{comments}
'''

# Comment ##########
COMMENT = '''***
{user} commented at {created_at}
({html_url})
***

{body}

'''