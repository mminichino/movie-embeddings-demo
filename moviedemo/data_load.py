#!/usr/bin/env python3

import sys
import time
from moviedemo.logformat import CustomLogFormatter
from moviedemo.google_transform import GoogleEmbedding
from cbcmgr.cb_transform import CBTransform
from moviedemo.check_image import CheckImage
from moviedemo.capella import create_bucket
import json
import logging
import warnings
import argparse

warnings.filterwarnings("ignore")
logger = logging.getLogger()
logging.getLogger("googleapiclient").setLevel(logging.ERROR)

file_handler = logging.FileHandler("run.log")
file_handler.setFormatter(CustomLogFormatter())
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def progress_bar(iteration, total, decimals=1, length=100, fill='#', errors=0, ops_per_sec=0.0, end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled = int(length * iteration // total)
    bar = fill * filled + '-' * (length - filled)
    print(f'\rProgress: |{bar}| {percent}% Complete - Errors: {errors} Ops/s: {ops_per_sec:.1f}', end=end)
    if iteration == total:
        print()


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-u', '--user', action='store', help="User Name", default="Administrator")
    parser.add_argument('-p', '--password', action='store', help="User Password", default="password")
    parser.add_argument('-h', '--host', action='store', help="Cluster Node Name", default="localhost")
    parser.add_argument('-b', '--bucket', action='store', help="Bucket", default="movies")
    parser.add_argument('-s', '--scope', action='store', help="Scope", default="data")
    parser.add_argument('-c', '--collection', action='store', help="Collection", default="data")
    parser.add_argument('-f', '--file', action='store', help="Data File", default="movie-data.json")
    parser.add_argument('-P', '--project', action='store', help="Project Name")
    parser.add_argument('-D', '--database', action='store', help="Capella Database")
    parser.add_argument('-R', '--profile', action='store', help="Capella API Profile", default="default")
    options = parser.parse_args()

    try:
        with open(options.file, 'r') as input_file:
            data = json.load(input_file)
    except FileNotFoundError:
        print(f"Data file {options.file} not found")
        sys.exit(1)

    try:
        GoogleEmbedding().get_text_embeddings("test")
    except Exception as err:
        print("Can not invoke GCP Vertex API. Check your GCP CLI auth settings and make sure the API is enabled.")
        print(f"Error: {err}")
        sys.exit(1)

    if options.project and options.database:
        create_bucket(options.profile, options.project, options.database, options.bucket, 1024, 1)

    keyspace = f"{options.bucket}.{options.scope}.{options.collection}"

    pool = CBTransform(options.host, options.user, options.password, ssl=True, quota=1024, create=True, replicas=1, keyspace=keyspace)

    data_length = len(data)
    progress_bar(0, data_length, length=50)
    for n, movie in enumerate(data):
        poster_url = movie['poster_path']

        if not movie['title'].isascii():
            continue

        result = CheckImage().check_image_url(poster_url)
        if not result or result not in ("BMP", "GIF", "JPEG", "PNG"):
            logger.error(f"Skipping \"{movie['title']}\" due to failed image check: Image type: {result}")
            continue

        pool.dispatch(movie, GoogleEmbedding)
        if pool.ops_per_sec > 1.75:
            ops_diff = pool.ops_per_sec - 1.75
            time.sleep(ops_diff)
        progress_bar(n + 1, data_length, length=50, errors=pool.error_count, ops_per_sec=pool.ops_per_sec)

    pool.join()
    pool.vector_index(f"movie_vector", 1408, "image_embedding")


if __name__ == '__main__':
    main()
