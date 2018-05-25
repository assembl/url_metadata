# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html
# licence: AGPL
# author: Amen Souissi

import re
import json
import urllib
from bs4 import BeautifulSoup


def extract_wikipedia_metadata(endpoint, url, **kwargs):
    result = {}
    try:
        parsed_uri = urllib.parse.urlparse(url)
        local = '{uri.netloc}'.format(uri=parsed_uri).split('.')[0]
        title = parsed_uri.path.split('/')[-1].replace('_',  '%20')
        # get metadata: use wikipedia api
        api_url = endpoint['url'].format(local=local, title=title)
        response = urllib.request.urlopen(api_url).read()
        data = json.loads(response.decode())
        pages = data.get('query', {}).get('pages', {})
        if pages:
            item = list(pages.items())[0][1]
            result['description'] = item.get('extract').replace('\n', '')

    except Exception:
        pass
    
    return result


def extract_twitter_metadata(endpoint, url, **kwargs):
    # we need to use the twitter API
    page = kwargs.get('page', None)
    result = {}
    soup = BeautifulSoup(page, "lxml")
    twit = soup.find('div', 'permalink-header')
    if twit:
        img = twit.find('img', 'avatar')
        if img:
            result = {'author_avatar': img['src']}

        username = twit.find('span', 'username')
        if username:
            name = username.find('b')
            if name:
                result['author_name'] = '@'+name.text

    return result


ENDPOINTS = [
    {
        'schemes': ["https://\\S*.wikipedia.org/wiki/\\S*"],
        'url': "https://{local}.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&explaintext=&exintro=&titles={title}",
        'extractor': extract_wikipedia_metadata
    },
    {
        'schemes': [
            "https://twitter.com/\\S*/status/\\S*",
            "https://\\S*.twitter.com/\\S*/status/\\S*"],
        'extractor': extract_twitter_metadata
    }
]


def extract_metadata(url, **kwargs):
    for endpoint in ENDPOINTS:
        if any([re.match(scheme, url) for scheme in endpoint['schemes']]):
            return endpoint['extractor'](endpoint, url, **kwargs)

    return {}