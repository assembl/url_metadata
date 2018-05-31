# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Ecreall and Bluenove under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html
# licence: AGPL
# author: Amen Souissi

import unittest
from micawber import *
from micawber.test_utils import test_pr

from utils import get_favicon_url, get_url_domain, get_url_metadata, pars_url_metadata


empty_document = '<html><head></head><body></body></html>'


def get_document(title, site_name, description, url, image, favicon):
    return '<html><head>' + \
        '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">' + \
        '<title>Site title Foo bar</title>' + \
        '<meta property="og:site_name" content="'+site_name+'">' + \
        '<meta property="og:type" content="website">' + \
        '<meta property="og:locale" content="fr_FR">' + \
        '<meta property="og:title" content="'+title+'">' + \
        '<meta property="og:description" content="'+description+'">' + \
        '<meta property="og:url" content="'+url+'">' + \
        '<meta property="og:image:type" content="image/png">' + \
        '<meta property="og:image:width" content="1880">' + \
        '<meta property="og:image:height" content="984">' + \
        '<meta property="og:image" content="'+image+'">' + \
        '<meta name="twitter:card" content="summary">' + \
        '<meta name="twitter:site" content="'+site_name+'">' + \
        '<meta name="twitter:url" content="'+url+'">' + \
        '<meta name="twitter:title" content="'+title+'">' + \
        '<meta name="twitter:description" content="'+description+'">' + \
        '<link rel="shortcut icon" href="'+favicon+'">'+ \
        '</head><body></body></html>'


class TestURLMetadata(unittest.TestCase):

    def test_get_favicon_url(self):
        url = 'http://link-test1'
        favicon = 'http://link-test1/favicon.ico'
        image = 'http://link-test1/foobar.png'
        title = 'FooBar title'
        site_name = 'FooBar'
        description = 'FooBar description'
        document = get_document(title, site_name, description, url, image, favicon)
        favicon_url = get_favicon_url(document, url)
        self.assertEqual(favicon_url, favicon)

    def test_get_favicon_url_empty_doc(self):
        url = 'http://link-test1'
        favicon_url = get_favicon_url(empty_document, url)
        self.assertIsNone(favicon_url)

    def test_get_url_domain(self):
        url = 'http://link-test1.com'
        domain = get_url_domain(url)
        self.assertEqual(domain, 'http://link-test1.com/')
        url = 'http://link-test1.com/foo/bar?re=1'
        domain = get_url_domain(url)
        self.assertEqual(domain, 'http://link-test1.com/')
        domain = get_url_domain(url, True)
        self.assertEqual(domain, 'link-test1')

    def test_pars_url_metadata(self):
        url = 'http://link-test1'
        favicon = 'http://link-test1/favicon.ico'
        image = 'http://link-test1/foobar.png'
        title = 'FooBar title'
        site_name = 'FooBar'
        description = 'FooBar description'
        document = get_document(title, site_name, description, url, image, favicon)
        metadata = pars_url_metadata(url, document.encode())
        expected = {
            'favicon_url': favicon,
            'description': description,
            'url': url,
            'title': title,
            'thumbnail_url': image,
            'provider_name': site_name
        }
        self.assertEqual(metadata, expected)

    def test_pars_url_metadata_empty_doc(self):
        url = 'http://link-test1'
        metadata = pars_url_metadata(url, empty_document.encode())
        expected = {
            'description': None,
            'thumbnail_url': None,
            'favicon_url': None,
            'url': 'http://link-test1',
            'title': None, 'provider_name':
            'link-test1'
        }
        self.assertEqual(metadata, expected)

    def test_get_url_metadata(self):
        url = 'http://video-test1'
        favicon = 'http://video-test1/favicon.ico'
        image = 'http://video-test1/foobar.png'
        title = 'FooBar title'
        site_name = 'FooBar'
        description = 'FooBar description'
        document = get_document(title, site_name, description, url, image, favicon)
        metadata = get_url_metadata(url, document.encode(), providers=test_pr)
        expected = {
            'favicon_url': favicon,
            'description': description,
            'url': url,
            'title': title,
            'thumbnail_url': image,
            'provider_name': site_name,
            'type': 'video',
            'html': '<test1>video</test1>'
        }
        self.assertEqual(metadata, expected)

    def test_get_url_metadata_empty_doc(self):
        url = 'http://video-test1'
        metadata = get_url_metadata(url, empty_document.encode(), providers=test_pr)
        expected = {
            'description': None,
            'thumbnail_url': None,
            'favicon_url': None,
            'url': 'http://video-test1',
            'title': None,
            'provider_name': 'video-test1',
            'type': 'video',
            'html': '<test1>video</test1>'
        }
        self.assertEqual(metadata, expected)

    def test_get_url_metadata_no_oembed(self):
        url = 'http://site-bar'
        favicon = 'http://site-bar/favicon.ico'
        image = 'http://site-bar/foobar.png'
        title = 'FooBar title'
        site_name = 'FooBar'
        description = 'FooBar description'
        document = get_document(title, site_name, description, url, image, favicon)
        metadata = get_url_metadata(url, document.encode(), providers=test_pr)
        expected = {
            'favicon_url': favicon,
            'description': description,
            'url': url,
            'title': title,
            'thumbnail_url': image,
            'provider_name': site_name
        }
        self.assertEqual(metadata, expected)