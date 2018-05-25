# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html
# licence: AGPL
# author: Amen Souissi

import sqlite3
import string
from flask import Flask, request, render_template, redirect, jsonify
from flask_cors import CORS, cross_origin
from sqlite3 import OperationalError
from urllib.parse import urlparse
import micawber

from utils import get_url_metadata, encode, decode


#Assuming urls.db is in your app root folder
app = Flask(__name__)

cors = CORS(app, resources={r"/": {"origins": "*"}})


def table_check():
    create_table_query = """
        CREATE TABLE URL_METADATA(
        ID INTEGER PRIMARY KEY     AUTOINCREMENT,
        METADATA TEXT NOT NULL UNIQUE,
        URL  TEXT  NOT NULL UNIQUE
        );
        """
    with sqlite3.connect('var/urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table_query)
        except OperationalError:
            pass


@app.route('/', methods=['GET', 'POST'])
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
def home():
    is_get = request.method == 'GET'
    with sqlite3.connect('var/urls.db') as conn:
        try:
            cursor = conn.cursor()
            # get the requested URL
            url = request.args.get('url', None) if \
                is_get else request.form.get('url', None)
            if url:
                # retrieve the metadata directly from the database if the URL already exists
                # else insert a new line in the database
                exist_url_query = """
                    SELECT METADATA FROM URL_METADATA
                        WHERE URL='{url}'
                    """.format(url=url)
                result_cursor = cursor.execute(exist_url_query)
                result_fetch = result_cursor.fetchone()
                if result_fetch:
                    url_metadata = decode(result_fetch[0])
                else:
                    url_metadata = get_url_metadata(url)
                    result_cursor = cursor.execute('SELECT max(ID) FROM URL_METADATA')
                    last_id = cursor.fetchone()[0] or 0
                    url_metadata['id'] = last_id
                    insert_row = """
                        INSERT INTO URL_METADATA (URL, METADATA)
                            VALUES ('{url}', '{metadata}')
                        """.format(url=url, metadata=encode(url_metadata))
                    cursor.execute(insert_row)
                
                # return the result to the user
                if is_get:
                    return jsonify(**{'code': 'SUCCESS',
                                      'metadata': url_metadata})
                else:
                    return render_template(
                        'home.html', url_metadata=url_metadata)

            return render_template('home.html')
        except Exception as error:
            if is_get:
                return jsonify(**{'code': 'ERROR',
                                  'error': str(error),
                                  'url': url
                                  })
            else:
                return render_template(
                    'home.html',
                    error=True)


if __name__ == '__main__':
    # This code checks whether database table is created or not
    table_check()
    # app.run(debug=True)
    app.run(host='0.0.0.0')
