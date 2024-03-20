#!/usr/bin/env python3
##
##

import logging
import argparse
from cbcmgr.cb_operation_s import CBOperation
from google_embedding import GoogleEmbedding
from flask import Flask
from flask import render_template
from flask import send_file
from flask import request
from waitress import serve

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return send_file("images/favicon.ico", mimetype='image/x-icon')


@app.route("/results", methods=['POST'])
def results():
    question = request.form['question']
    app.logger.info(f"asked question {question}")

    vector = GoogleEmbedding().get_text_embeddings(question)

    movies = op.vector_search('movie_vector', 'image_embedding', vector)

    return render_template("results.html", result_list=movies)


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-P', '--port', action='store', default=8080)
    parser.add_argument('-u', '--user', action='store', help="User Name", default="Administrator")
    parser.add_argument('-p', '--password', action='store', help="User Password", default="password")
    parser.add_argument('-h', '--host', action='store', help="Cluster Node Name", default="localhost")
    parser.add_argument('-b', '--bucket', action='store', help="Bucket", default="movies")
    parser.add_argument('-s', '--scope', action='store', help="Scope", default="data")
    parser.add_argument('-c', '--collection', action='store', help="Collection", default="data")
    parser.add_argument('-d', '--debug', action='store_true', help="Debug")
    parser.add_argument('-?', action='help')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    options = parse_args()
    keyspace = f"{options.bucket}.{options.scope}.{options.collection}"
    op = CBOperation(options.host, options.user, options.password, ssl=True, quota=1024, create=True, replicas=0)
    op.connect(keyspace)
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(app, host='0.0.0.0', port=options.port)
