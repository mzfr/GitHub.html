import os
from datetime import datetime, timedelta
import requests
import requests_cache
from jinja2 import Environment, FileSystemLoader

expire_after = timedelta(hours=1)
requests_cache.install_cache('github', expire_after=expire_after)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SEARCH = "https://api.github.com/search/issues?q=type:"


def main():
    username = input("Enter a username: ")
    source, fork = get_repos(username)
    pr = get_all_pulls(username)
    issues = get_all_issues(username)

    j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
    data = j2_env.get_template('template.html').render(source=source, fork=fork, issue=issues, pull=pr)

    with open('info.html', 'w', encoding="utf-8") as f:
        f.write(data.encode('ascii', 'ignore').decode('ascii'))


def get_repos(username):
    url = "https://api.github.com/users/{username}/repos?per_page=100".format(username=username)
    data = requests.get(url).json()
    source = []
    fork = []
    for repo in data:
        name = repo['name']
        description = repo['description']
        created = repo['created_at'][:10]
        update = repo['pushed_at'][:10]
        lang = repo['language']
        url = repo['html_url']
        stars = repo['stargazers_count']
        if repo['fork']:
            fork.append([name, description, created, update, lang, stars, url])
        else:
            source.append([name, description, created, update, lang, stars, url])

    return source, fork


def get_all_issues(username):

    def useful_info(issue_json):
        return [
            [
                issue['title'], issue['comments'],
                issue['created_at'][:10], issue['html_url']
            ]
            for issue in issue_json['items']
        ]

    url = SEARCH + "issue+author:{username}%20&sort=created&per_page=100".format(username=username)
    all_issue = []

    resp = requests.get(url)
    all_issue.extend(useful_info(resp.json()))

    while 'next' in resp.links:
        resp = requests.get(resp.links['next']['url'])
        all_issue.extend(useful_info(resp.json()))

    return all_issue


def get_all_pulls(username):

    def useful_info(pulls_json):
        return [
            [
                pr['title'], pr['created_at'][:10],
                pr['author_association'], pr['html_url']
            ]
            for pr in pulls_json['items']
        ]

    url = SEARCH + "pr+author:{username}%20&sort=created&per_page=100".format(username=username)
    all_pulls = []

    resp = requests.get(url)
    all_pulls.extend(useful_info(resp.json()))

    while 'next' in resp.links:
        resp = requests.get(resp.links['next']['url'])
        all_pulls.extend(useful_info(resp.json()))

    return all_pulls


if __name__ == '__main__':
    main()
