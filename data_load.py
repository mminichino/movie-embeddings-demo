#!/usr/bin/env python3

import time
from logformat import CustomLogFormatter
from google_transform import GoogleEmbedding
from cbcmgr.cb_transform import CBTransform
from check_image import CheckImage
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

data_file = "movie-data-2023.json"


def progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='#', end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled = int(length * iteration // total)
    bar = fill * filled + '-' * (length - filled)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=end)
    if iteration == total:
        print()


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-u', '--user', action='store', help="User Name", default="Administrator")
parser.add_argument('-p', '--password', action='store', help="User Password", default="password")
parser.add_argument('-h', '--host', action='store', help="Cluster Node Name", default="localhost")
parser.add_argument('-b', '--bucket', action='store', help="Bucket", default="movies")
parser.add_argument('-s', '--scope', action='store', help="Scope", default="data")
parser.add_argument('-c', '--collection', action='store', help="Collection", default="data")
options = parser.parse_args()

with open(data_file, 'r') as input_file:
    data = json.load(input_file)

keyspace = f"{options.bucket}.{options.scope}.{options.collection}"

pool = CBTransform(options.host, options.user, options.password, ssl=True, quota=1024, create=True, replicas=0, keyspace=keyspace)

average_duration = 0
total_duration = 0
data_length = len(data)
progress_bar(0, data_length, prefix='Progress:', suffix='Complete', length=50)
for n, movie in enumerate(data):
    poster_url = movie['poster_path']

    result = CheckImage().check_image_url(poster_url)
    if not result or result not in ("BMP", "GIF", "JPEG", "PNG"):
        logger.error(f"Skipping \"{movie['title']}\" due to failed image check: Image type: {result}")
        continue

    pool.dispatch(movie, GoogleEmbedding)
    time.sleep(0.5)
    progress_bar(n + 1, data_length, prefix='Progress:', suffix='Complete', length=50)

pool.join()

# duration_string = time.strftime("%H hours %M minutes %S seconds.", time.gmtime(total_duration))
# average_string = time.strftime("%H hours %M minutes %S seconds.", time.gmtime(average_duration))
# logger.info(f"Embedding completed in {duration_string} [Average per embedding: {average_string}]")
