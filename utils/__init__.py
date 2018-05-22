# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Ecreall under licence AGPL terms
# avalaible on http://www.gnu.org/licenses/agpl.html
# licence: AGPL
# author: Amen Souissi

import json
import micawber
import metadata_parser
import urllib
import requests
from bs4 import BeautifulSoup

from .apis_endpoints import extract_metadata


special_characters = [('\'', '#')]

# Some hosts don't like the requests default UA. Use this one instead.
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 \
        Safari/537.36'
}


oembed_providers_reg = micawber.ProviderRegistry()


with open('./providers.json') as providers_file:
    providers = json.load(providers_file)
    for provider in providers:
        endpoints = provider['endpoints']
        for endpoint in endpoints:
            url = endpoint['url']
            schemes = endpoint['schemes']
            for scheme in schemes:
                oembed_providers_reg.register(scheme, micawber.Provider(url))


oembed_providers = micawber.bootstrap_basic(registry=oembed_providers_reg)


#inspired: https://github.com/phillipsm/pyfav/blob/master/pyfav/pyfav.py
def get_favicon_url(markup, url):
    """
    Given markup, parse it for a favicon URL. The favicon URL is adjusted
    so that it can be retrieved independently. We look in the markup returned
    from the URL first and if we don't find a favicon there, we look for the 
    default location, e.g., http://example.com/favicon.ico . We retrurn None if
    unable to find the file.
    
    Keyword arguments:
    markup -- A string containing the HTML markup.
    url -- A string containing the URL where the supplied markup can be found.
    We use this URL in cases where the favicon path in the markup is relative.
    
    Retruns:
    The URL of the favicon. A string. If not found, returns None.
    """
    
    parsed_site_uri = urllib.parse.urlparse(url)
    
    soup = BeautifulSoup(markup, "lxml")
        
    # Do we have a link element with the icon?
    icon_link = soup.find('link', rel='icon')
    favicon_url = None
    if icon_link and icon_link.has_attr('href'):
        
        favicon_url = icon_link['href']
        
        # Sometimes we get a protocol-relative path
        if favicon_url.startswith('//'):
            parsed_uri = urllib.parse.urlparse(url)
            favicon_url = parsed_uri.scheme + ':' + favicon_url

        # An absolute path relative to the domain
        elif favicon_url.startswith('/'):
            favicon_url = parsed_site_uri.scheme + '://' + \
                parsed_site_uri.netloc + favicon_url
        
        # A relative path favicon    
        elif not favicon_url.startswith('http'):
            path, filename  = os.path.split(parsed_site_uri.path)
            favicon_url = parsed_site_uri.scheme + '://' + \
                parsed_site_uri.netloc + '/' + os.path.join(path, favicon_url)
        
        # We found a favicon in the markup and we've formatted the URL
        # so that it can be loaded independently of the rest of the page

    if favicon_url:
        return favicon_url
        
    # The favicon doesn't appear to be in the makrup
    # Let's look at the common locaiton, url/favicon.ico
    favicon_url = '{uri.scheme}://{uri.netloc}/favicon.ico'.format(\
        uri=parsed_site_uri)
                        
    response = requests.get(favicon_url, headers=headers)
    if response.status_code == requests.codes.ok:
        return favicon_url

    # No favicon in the markup or at url/favicon.ico
    return None


def get_url_domain(url, name_only=False):
    parsed_uri = urllib.parse.urlparse(url)
    if not name_only:
        return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    return '{uri.netloc}'.format(uri=parsed_uri).replace('www.', '').split('.')[0]


def pars_url_metadata(url):
    page = ''
    try:
        resp = urllib.request.urlopen(
            urllib.request.Request(url, headers=headers))
        url = resp.url
        page = resp.read()
        url_metadata = metadata_parser.MetadataParser(
            html=page.decode('utf-8'), requests_timeout=100)
    except Exception:
        return None
    
    image = url_metadata.get_metadata('image', None)
    if not image:
        image = url_metadata.get_metadata('image:src', None)

    site_name = url_metadata.get_metadata('site_name', None)
    if not site_name:
        site_name = url_metadata.get_metadata('og:site_name', None)
        site_name = site_name if site_name else get_url_domain(url, True)

    result = {
        'url': url,
        'favicon_url': get_favicon_url(page, url),
        'title': url_metadata.get_metadata('title', None),
        'description': url_metadata.get_metadata('description', None),
        'provider_name': site_name,
        'thumbnail_url': image,
        'html': None
    }
    result.update(extract_metadata(url, page=page))
    return result


def get_url_metadata(url):
    url_metadata = pars_url_metadata(url)
    try:
        provider_metadata = oembed_providers.request(url)
        url_metadata.update(provider_metadata)
        return provider_metadata
    except Exception:
        return url_metadata


def encode(data_dict):
    result = json.dumps(data_dict)
    for special_character, code in special_characters:
        result = result.replace(special_character, code)

    return result


def decode(data_str):
    result = data_str
    for special_character, code in special_characters:
        result = result.replace(code, special_character)

    return json.loads(data_str)