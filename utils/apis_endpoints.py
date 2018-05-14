# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Ecreall under licence AGPL terms
# avalaible on http://www.gnu.org/licenses/agpl.html
# licence: AGPL
# author: Amen Souissi

import re
import json
import urllib


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


ENDPOINTS = [
    {
        'scheme': "https://\\S*.wikipedia.org/wiki/\\S*",
        'url': "https://{local}.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&explaintext=&exintro=&titles={title}",
        'extractor': extract_wikipedia_metadata
    }
]


def extract_metadata(url, **kwargs):
    for endpoint in ENDPOINTS:
        if re.match(endpoint['scheme'], url):
            return endpoint['extractor'](endpoint, url, **kwargs)

    return {}