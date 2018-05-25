import argparse
import re
from urllib import request, parse
import json
from datetime import datetime


def print_commit_counts(owner, repo):
    """
    Prints the number of commits for the first top 30 contributors
    :param owner: Owner
    :param repo: Repository name
    """
    url = 'https://api.github.com/repos/{}/{}/stats/contributors'.format(owner, repo)
    response = request.urlopen(url)
    data_bytes = response.read()
    json_data = data_bytes.decode('utf-8')
    data = json.loads(json_data)
    zip_data = [(item['author']['login'], item['total']) for item in data]
    sort_data = sorted(zip_data, key=lambda x: x[1], reverse=True)[:30]
    row_names = ('Login', 'Commit counts')
    row_format = "{:<15}" * (len(row_names))
    print(row_format.format(*row_names))
    print('_' * 30)
    for row in sort_data:
        print(row_format.format(*row))


def get_number_of_questions(url):
    number_questions = 0
    while True:
        response = request.urlopen(url)
        data_bytes = response.read()
        json_data = data_bytes.decode('utf-8')
        data = json.loads(json_data)
        number_questions += len(data)
        try:
            links = response.headers.get('Link').split(',')
        except AttributeError:
            break
        actions = {}
        for link in links:
            url, action = re.search('<(.*?)>; rel="(.*?)"', link).groups()
            actions[action] = url
        if 'next' in actions.keys():
            url = actions['next']
        else:
            break
    return number_questions


def print_number_pull_request(owner, repo):
    """
    Print number of pull request
    :param owner: Owner
    :param repo: Repository name
    """
    url = 'https://api.github.com/repos/{}/{}/pulls?state=open&per_page=100'.format(owner, repo)
    open_pull_request = get_number_of_questions(url)
    print('Number of open pull request: ', open_pull_request)
    url = 'https://api.github.com/repos/{}/{}/pulls?state=closed&per_page=100'.format(owner, repo)
    closed_pull_request = get_number_of_questions(url)
    print('Number of closed pull request: ', closed_pull_request)


def get_number_of_old_questions(url, number_day):
    number_questions = 0
    now_date = datetime.now()
    while True:
        response = request.urlopen(url)
        data_bytes = response.read()
        json_data = data_bytes.decode('utf-8')
        data = json.loads(json_data)
        for pr in data:
            create_date = datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            date = now_date - create_date
            number_days = date.days
            if number_days > number_day:
                number_questions += 1
        try:
            links = response.headers.get('Link').split(',')
        except AttributeError:
            break
        actions = {}
        for link in links:
            url, action = re.search('<(.*?)>; rel="(.*?)"', link).groups()
            actions[action] = url
        if 'next' in actions.keys():
            url = actions['next']
        else:
            break
    return number_questions


def print_number_of_old_pull_request(owner, repo):
    """
    Print number of old pull request
    :param owner: Owner
    :param repo: Repository name
    """
    url = 'https://api.github.com/repos/{}/{}/pulls?state=open&per_page=100'.format(owner, repo)
    number_pull_request = get_number_of_old_questions(url, 30)
    print('Number of old pull request: ', number_pull_request)


def print_number_issues(owner, repo):
    """
    Print number of issues
    :param owner: Owner
    :param repo: Repository name
    """
    url = 'https://api.github.com/repos/{}/{}/issues?state=open&per_page=100'.format(owner, repo)
    open_issues = get_number_of_questions(url)
    print('Number of open issues: ', open_issues)
    url = 'https://api.github.com/repos/{}/{}/issues?state=closed&per_page=100'.format(owner, repo)
    closed_issues = get_number_of_questions(url)
    print('Number of closed issues: ', closed_issues)


def print_number_of_old_issues(owner, repo):
    """
    Print number of old issues
    :param owner: Owner
    :param repo: Repository name
    """
    url = 'https://api.github.com/repos/{}/{}/issues?state=open&per_page=100'.format(owner, repo)
    number_issues = get_number_of_old_questions(url, 14)
    print('Number of old issues: ', number_issues)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GitHub repository analysis.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--url', help='public repository on github.com', required=True)
    parser.add_argument('--data_start', help='analysis start date')
    parser.add_argument('--data_stop', help='analysis end date')
    parser.add_argument('--branch', help='branch of the repository', default='master')
    args = parser.parse_args()
    _, owner, repo = parse.urlparse(args.url).path.split('/')
    print_commit_counts(owner, repo)
    print_number_pull_request(owner, repo)
    print_number_of_old_pull_request(owner, repo)
    print_number_issues(owner, repo)
    print_number_of_old_issues(owner, repo)