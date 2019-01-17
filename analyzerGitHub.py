import argparse
import re
import json
from urllib import request, parse, error
from datetime import datetime
from collections import defaultdict

from config import *


def parser_url(**kwargs):
    path = PATH.format(owner=kwargs.pop('owner'),
                       repo=kwargs.pop('repo'),
                       info=kwargs.pop('info'))
    query = '&'.join([QUERY.format(
        key, kwargs[key]) for key in kwargs])
    url = parse.urlunparse((SCHEME, HOSTNAME, path, PARAMS, query, FRAGMENT))
    return url


def get_response_pagination(url):
    response = request.urlopen(url)
    data_bytes = response.read()
    json_data = data_bytes.decode('utf-8')
    data = json.loads(json_data)
    try:
        links = response.headers.get('Link').split(',')
    except AttributeError:
        return data, None
    actions = {}
    for link in links:
        url, action = re.search('<(.*?)>; rel="(.*?)"', link).groups()
        actions[action] = url
    if 'next' in actions.keys():
        url = actions['next']
        return data, url
    else:
        return data, None


def print_commit_counts(**kwargs):
    url = parser_url(**kwargs)
    all_data = []
    while True:
        data, url = get_response_pagination(url)
        all_data.extend(data)
        if url is None:
            break
    zip_data = defaultdict(int)
    for item in all_data:
        try:
            zip_data[item['author']['login']] += 1
        except TypeError:
            zip_data['Unknown'] += 1
    sort_data = sorted(zip_data.items(), key=lambda x: x[1], reverse=True)[:30]
    row_names = ('Login', 'Commit counts')
    row_format = "{:<25}" * (len(row_names))
    print(row_format.format(*row_names))
    print('_' * 30)
    for row in sort_data:
        print(row_format.format(*row))


def get_number_of_questions(url, since, until):
    number_questions = 0
    while True:
        data, url = get_response_pagination(url)
        for pull in data:
            if since and until:
                create_date = datetime.strptime(pull['created_at'],
                                                DATA_FORMAT)
                since_date = datetime.strptime(since,
                                               DATA_FORMAT)
                until_date = datetime.strptime(until,
                                               DATA_FORMAT)
                if since_date <= create_date <= until_date:
                    number_questions += 1
            elif since:
                create_date = datetime.strptime(pull['created_at'],
                                                DATA_FORMAT)
                since_date = datetime.strptime(since,
                                               DATA_FORMAT)
                if since_date <= create_date:
                    number_questions += 1
            elif until:
                create_date = datetime.strptime(pull['created_at'],
                                                DATA_FORMAT)
                until_date = datetime.strptime(until, DATA_FORMAT)
                if create_date <= until_date:
                    number_questions += 1
            else:
                number_questions += 1
        if url is None:
            break
    return number_questions


def print_number_pull_request(**kwargs):
    since = kwargs.pop('since')
    until = kwargs.pop('until')
    params_open_pull_request = kwargs.copy()
    params_open_pull_request.update({'state': 'open'})
    open_pull_request = get_number_of_questions(
        parser_url(**params_open_pull_request), since, until)
    print('Number of open pull request: ', open_pull_request)
    params_closed_pull_request = kwargs.copy()
    params_closed_pull_request.update({'state': 'closed'})
    closed_pull_request = get_number_of_questions(
        parser_url(**params_closed_pull_request), since, until)
    print('Number of closed pull request: ', closed_pull_request)


def get_number_of_old_questions(url, number_day, since, until):
    number_questions = 0
    now_date = datetime.now()
    while True:
        data, url = get_response_pagination(url)
        for pull in data:
            if since and until:
                create_date = datetime.strptime(pull['created_at'],
                                                DATA_FORMAT)
                since_date = datetime.strptime(since,
                                               DATA_FORMAT)
                until_date = datetime.strptime(until,
                                               DATA_FORMAT)
                if since_date <= create_date <= until_date:
                    date = now_date - create_date
                    number_days = date.days
                    if number_days > number_day:
                        number_questions += 1
            elif since:
                create_date = datetime.strptime(pull['created_at'],
                                                DATA_FORMAT)
                since_date = datetime.strptime(since, DATA_FORMAT)
                if since_date <= create_date:
                    date = now_date - create_date
                    number_days = date.days
                    if number_days > number_day:
                        number_questions += 1
            elif until:
                create_date = datetime.strptime(pull['created_at'],
                                                DATA_FORMAT)
                until_date = datetime.strptime(until, DATA_FORMAT)
                if create_date <= until_date:
                    date = now_date - create_date
                    number_days = date.days
                    if number_days > number_day:
                        number_questions += 1
            else:
                create_date = datetime.strptime(pull['created_at'],
                                                DATA_FORMAT)
                date = now_date - create_date
                number_days = date.days
                if number_days > number_day:
                    number_questions += 1
        if url is None:
            break
    return number_questions


def print_number_of_old_pull_request(**kwargs):
    since = kwargs.pop('since')
    until = kwargs.pop('until')
    kwargs.update({'state': 'open'})
    number_pull_request = get_number_of_old_questions(
        parser_url(**kwargs), 30, since, until)
    print('Number of old pull request: ', number_pull_request)


def print_number_issues(**kwargs):
    since = kwargs.pop('since')
    until = kwargs.pop('until')
    params_open_issues = kwargs.copy()
    params_open_issues.update({'state': 'open'})
    open_issues = get_number_of_questions(
        parser_url(**params_open_issues), since, until)
    print('Number of open issues: ', open_issues)
    params_closed_issues = kwargs.copy()
    params_closed_issues.update({'state': 'closed'})
    closed_issues = get_number_of_questions(
        parser_url(**params_closed_issues), since, until)
    print('Number of closed issues: ', closed_issues)


def print_number_of_old_issues(**kwargs):
    since = kwargs.pop('since')
    until = kwargs.pop('until')
    kwargs.update({'state': 'open'})
    number_issues = get_number_of_old_questions(
        parser_url(**kwargs), 14, since, until)
    print('Number of old issues: ', number_issues)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='GitHub repository analysis.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--url',
        help='public repository on github.com',
        required=True)
    parser.add_argument(
        '--since',
        help='analysis start date. This is a timestamp in ISO 8601 format:'
             ' YYYY-MM-DDTHH:MM:SSZ',
        default=argparse.SUPPRESS)
    parser.add_argument(
        '--until',
        help='analysis end date. This is a timestamp in ISO 8601 format:'
             ' YYYY-MM-DDTHH:MM:SSZ',
        default=argparse.SUPPRESS)
    parser.add_argument(
        '--branch',
        help='branch of the repository',
        default='master')
    args = parser.parse_args()
    parameters = args.__dict__
    url = parameters.pop('url')
    branch = parameters.pop('branch')
    _, owner, repo = parse.urlparse(url).path.split('/')
    parameters.update({'owner': owner, 'repo': repo, 'per_page': 100})
    try:
        params_commit_counts = parameters.copy()
        params_commit_counts.update({'info': 'commits', 'sha': branch})
        print_commit_counts(**params_commit_counts)

        params_pull_request = parameters.copy()
        params_pull_request.update({'info': 'pulls', 'base': branch})
        print_number_pull_request(**params_pull_request)

        params_old_pull_request = parameters.copy()
        params_old_pull_request.update({'info': 'pulls', 'base': branch})
        print_number_of_old_pull_request(**params_old_pull_request)

        params_issues = parameters.copy()
        params_issues.update({'info': 'issues'})
        print_number_issues(**params_issues)

        params_old_issues = parameters.copy()
        params_old_issues.update({'info': 'issues'})
        print_number_of_old_issues(**params_old_issues)
    except error.HTTPError:
        print("API rate limit exceeded. (But here's the good news:"
              " Authenticated requests get a higher rate limit."
              " Check out the documentation for more details.)")
    except ValueError:
        print("Bad format a timestamp. "
              "Use the flag -h or --help when starting the script.")
