# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Ecreall and Bluenove under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html
# licence: AGPL
# author: Amen Souissi

import io
import sqlite3
import hashlib
import urllib
import json
import magic
from flask import (
    Flask, request, render_template,
    jsonify, send_file, abort)
from flask_cors import CORS, cross_origin
from sqlite3 import OperationalError

from utils import get_url_metadata, headers


#Assuming urls.db is in your app root folder
app = Flask(__name__)

cors = CORS(app, resources={r"/": {"origins": "*"}})

DB_FILENAME = 'var/urls.db'


def table_check():
    create_table_query = """
        CREATE TABLE URL_METADATA(
        ID INTEGER PRIMARY KEY     AUTOINCREMENT,
        METADATA TEXT NOT NULL UNIQUE,
        URL  TEXT  NOT NULL UNIQUE
        );
        """
    create_pictures_table_query = """
        CREATE TABLE PICTURES(
        ID TEXT PRIMARY KEY,
        PICTURE BLOB
        );
        """
    with sqlite3.connect(DB_FILENAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table_query)
        except OperationalError:
            pass

        try:
            cursor.execute(create_pictures_table_query)
        except OperationalError:
            pass


def get_picture_uploader(cursor):
    def insert_picture(url):
        try:
            # read the picture from the URL
            blob = urllib.request.urlopen(
                urllib.request.Request(url, headers=headers)).read()
            # generate an id for this URL
            img_id = hashlib.sha256(url.encode('utf-8')).hexdigest()
            exist_img_query = """
                SELECT PICTURE FROM PICTURES
                    WHERE ID='{img_id}'
                """.format(img_id=img_id)
            result_cursor = cursor.execute(exist_img_query)
            result_fetch = result_cursor.fetchone()
            # if the picture exist return the img_id else add it to the database
            if not result_fetch:
                add_img_query = """INSERT INTO PICTURES
                (ID, PICTURE)
                VALUES(?, ?);"""
                cursor.execute(add_img_query, [img_id, sqlite3.Binary(blob)])

            return img_id
        except Exception:
            return None

    return insert_picture


@app.route('/', methods=['GET', 'POST'])
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
def home():
    is_get = request.method == 'GET'
    with sqlite3.connect(DB_FILENAME) as conn:
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
                    url_metadata = json.loads(result_fetch[0])
                else:
                    url_metadata = get_url_metadata(
                        url, picture_uploader=get_picture_uploader(cursor))
                    result_cursor = cursor.execute('SELECT max(ID) FROM URL_METADATA')
                    last_id = cursor.fetchone()[0] or 0
                    url_metadata['id'] = last_id
                    insert_row = """
                        INSERT INTO URL_METADATA (URL, METADATA)
                            VALUES (?, ?)
                        """
                    cursor.execute(insert_row, [url, json.dumps(url_metadata)])

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


# A view to serve the images
@app.route('/picture/<picture_id>')
def picture(picture_id):
    with sqlite3.connect(DB_FILENAME) as conn:
        try:
            cursor = conn.cursor()
            exist_img_query = """
                SELECT PICTURE FROM PICTURES
                    WHERE ID='{img_id}'
                """.format(img_id=picture_id)
            result_cursor = cursor.execute(exist_img_query)
            result_fetch = result_cursor.fetchone()
            if result_fetch:
                fp = io.BytesIO(result_fetch[0])
                mimetype = magic.from_buffer(fp.read(), mime=True)
                fp.seek(0)
                return send_file(fp, mimetype=mimetype)

            return abort(404)
        except Exception as error:
            return abort(404)


if __name__ == '__main__':
    # This code checks whether database table is created or not
    table_check()
    # app.run(debug=True)
    app.run(host='0.0.0.0')
