# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Ecreall and Bluenove under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html
# licence: AGPL
# author: Amen Souissi

from os.path import dirname, join
import json
import micawber
import metadata_parser
import os.path
import urllib
import requests
from flask import url_for
from bs4 import BeautifulSoup

from .apis_endpoints import extract_metadata


# all the pictures present in the URL metadata
pictures = ['thumbnail', 'thumbnail_url', 'author_avatar', 'favicon_url']

# Some hosts don't like the requests default UA. Use this one instead.
headers = {
    'User-Agent': 'Mozilla/5.0'
}


oembed_providers_reg = micawber.ProviderRegistry()
providers_fname = join(dirname(__file__), 'providers.json')

with open(providers_fname) as providers_file:
    providers = json.load(providers_file)
    for provider in providers:
        for endpoint in provider['endpoints']:
            for scheme in endpoint['schemes']:
                oembed_providers_reg.register(
                    scheme, micawber.Provider(endpoint['url']))


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

    try:
        # The favicon doesn't appear to be in the markup
        # Let's look at the common location, url/favicon.ico
        favicon_url = '{uri.scheme}://{uri.netloc}/favicon.ico'.format(\
            uri=parsed_site_uri)
        response = requests.get(favicon_url, headers=headers)
        if response.status_code == requests.codes.ok:
            return favicon_url
    except Exception:
        pass


    # No favicon in the markup or at url/favicon.ico
    return None


def get_url_domain(url, name_only=False):
    """
    Return the domain of an URL. If name_only is True,
    we return only the netloc of the URL
    """
    parsed_uri = urllib.parse.urlparse(url)
    if not name_only:
        return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    return '{uri.netloc}'.format(uri=parsed_uri).replace('www.', '').split('.')[0]


def parse_url_metadata(url, html=None):
    """
    This function parses the HTML page and retrieves the URL metadata using MetadataParser API.
    """
    page = html
    original_url = url
    try:
        if not html:
            # Reading the HTML page and retrieving metadata
            resp = urllib.request.urlopen(
                urllib.request.Request(original_url, headers=headers))
            # Retrieve the original URL. The URL can be shortened by an URL shortener like bitly
            original_url = resp.url
            page = resp.read()
        url_metadata = metadata_parser.MetadataParser(
            html=page.decode('utf-8'), requests_timeout=100)
    except Exception:
        return None

    # Formatting and verification of metadata
    thumbnail_url = url_metadata.get_metadata('image', None)
    if not thumbnail_url:
        thumbnail_url = url_metadata.get_metadata('image:src', None)

    site_name = url_metadata.get_metadata('site_name', None)
    if not site_name:
        site_name = url_metadata.get_metadata('og:site_name', None)
        site_name = site_name if site_name else get_url_domain(original_url, True)

    result = {
        'url': original_url,
        'favicon_url': get_favicon_url(page, original_url),
        'title': url_metadata.get_metadata('title', None),
        'description': url_metadata.get_metadata('description', None),
        'provider_name': site_name,
        'thumbnail_url': thumbnail_url
    }
    result.update(extract_metadata(original_url, page=page))
    return result


def get_url_metadata(url, html=None, picture_uploader=None, providers=oembed_providers):
    """
    Retrieving URL metadata by applying the MetadataParser API and the oembed API.
    picture_uploader is used to save the images in the database
    """
    url_metadata = parse_url_metadata(url, html)
    try:
        # retrieve the original URL. The URL can be shortened by an URL shortener like bitly
        original_url = url_metadata['url'] or url
        provider_metadata = providers.request(original_url)
        provider_metadata.update(url_metadata)
        url_metadata = provider_metadata
    except Exception:
        pass

    # Recovery of the author's picture
    author_name = url_metadata.get('author_name', None)
    author_url = url_metadata.get('author_url', None)
    author_avatar = url_metadata.get('author_avatar', None)
    if not author_avatar and author_name and author_url:
        author_metadata = get_url_metadata(author_url, providers=providers)
        url_metadata['author_avatar'] = author_metadata.get(
            'thumbnail_url', None) if author_metadata else None

    # Save the pictures in the database (see picture_uploader)
    if picture_uploader:
        for picture in pictures:
            picture_url = url_metadata.get(picture, None)
            if picture_url:
                picture_id = picture_uploader(picture_url)
                url_metadata[picture] = url_for(
                    'picture',
                    picture_id=picture_id) if picture_id else None


    return url_metadata
