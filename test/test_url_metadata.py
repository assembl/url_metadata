# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Ecreall and Bluenove under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html
# licence: AGPL
# author: Amen Souissi

import unittest
import os
import sqlite3
from micawber.test_utils import test_pr

import url_metadata


class TestURLMetadata(unittest.TestCase):

    def setUp(self):
        self.DB_FILENAME = "test/tmp_urls.db"
        url_metadata.DB_FILENAME = self.DB_FILENAME
        self.conn = sqlite3.connect(self.DB_FILENAME)
        self.select_tables = """
        SELECT
            name
        FROM
            sqlite_master
        WHERE
            type = 'table' AND
            name NOT LIKE 'sqlite_%';
        """
        
    def get_tables(self):
        return self.conn.execute(self.select_tables).fetchall()

    def tearDown(self):
        self.conn.close()
        os.remove(self.DB_FILENAME)

    def test_check_tables(self):
        tables = self.get_tables()
        self.assertListEqual(tables, [])

        url_metadata.table_check()

        tables = self.get_tables()
        self.assertListEqual(tables, [('URL_METADATA',), ('PICTURES',)])

    def test_check_tables_existing(self):
        tables = self.get_tables()
        self.assertListEqual(tables, [])

        url_metadata.table_check()

        tables = self.get_tables()
        self.assertListEqual(tables, [('URL_METADATA',), ('PICTURES',)])

        url_metadata.table_check()

        tables = self.get_tables()
        self.assertListEqual(tables, [('URL_METADATA',), ('PICTURES',)])
