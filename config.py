URLS = {
    'url_commits': 'https://api.github.com/repos/{}/{}/commits?'
                   'since={}&until={}&sha={}&per_page=100',
    'url_pull_request': 'https://api.github.com/repos/{}/{}/pulls?'
                        'state=open&base={}&per_page=100',
    'url_issues': 'https://api.github.com/repos/{}/{}/issues?'
                  'state=open&per_page=100'
}

DATA_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

SCHEME = 'https'
HOSTNAME = 'api.github.com'
PATH = 'repos/{owner}/{repo}/{info}'
PARAMS = ''
QUERY = '{}={}'
FRAGMENT = ''

DESCRIPTION = {''}
