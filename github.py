import os
from datetime import datetime, timedelta
import requests
import requests_cache
from jinja2 import Environment, FileSystemLoader

expire_after = timedelta(hours=1)
requests_cache.install_cache('github', expire_after=expire_after)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    source, fork = get_repos()
    pr = get_pulls()
    issues = get_issues()

    j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
    data = j2_env.get_template('template.html').render(source=source, fork=fork, issue=issues, pull=pr)

    with open('DZ-info.html', 'w', encoding="utf-8") as f:
        f.write(data.encode('ascii', 'ignore').decode('ascii'))


def get_repos():
    url = "https://api.github.com/users/dufferzafar/repos?per_page=100"
    data = requests.get(url).json()
    fcount = 0
    Scount = 0
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
            fork.append([fcount, name, description, created, update, lang, stars, url])
            fcount += 1
        else:
            source.append([Scount, name, description, created, update, lang, stars, url])
            Scount += 1

    return source, fork


def get_all_issues():
    url = "https://api.github.com/search/issues?q=type:issue+author:dufferzafar%20&sort=created&per_page=100"
    issues = requests.get(url).json()
    all_issue = []
    for i, issue in enumerate(issues['items']):
        title = issue['title']
        comments = issue['comments']
        created = issue['created_at'][:10]
        url = issue['html_url']
        all_issue.append([i, title, comments, created, url])

    return all_issue


def get_all_pulls():
    url = "https://api.github.com/search/issues?q=type:pr+author:dufferzafar%20&sort=created&per_page=100"
    # https://api.github.com/search/issues?q=type:pr+author:dufferzafar%20&sort=created&per_page=100&page=2
    pulls = requests.get(url).json()
    all_pulls = []
    for i, pr in enumerate(pulls['items']):
        title = pr['title']
        created = pr['created_at'][:10]
        association = pr['author_association']
        url = pr['html_url']
        all_pulls.append([i, title, created, association, url])

    return all_pulls


if __name__ == '__main__':
    main()
