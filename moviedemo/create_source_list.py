#!/usr/bin/env python3

import logging
import json
import warnings
import time
from restmgr import RESTManager
from logformat import CustomDisplayFormatter

warnings.filterwarnings("ignore")
logger = logging.getLogger()
hostname = "api.themoviedb.org"
token_file = "tmdb.key"
year = 2023
output_file = f"movie-data-{year}.json"

screen_handler = logging.StreamHandler()
screen_handler.setFormatter(CustomDisplayFormatter())
logger.addHandler(screen_handler)
logger.setLevel(logging.INFO)

rest = RESTManager(hostname=hostname, token_file=token_file)

start_time = time.perf_counter()
movies = rest.get_tmdb_py_year(year)
end_time = time.perf_counter()

record_count = len(movies)
run_duration = end_time - start_time
duration_string = time.strftime("%H hours %M minutes %S seconds.", time.gmtime(run_duration))
ops_per_s = record_count / run_duration
logger.info(f"Export completed in {duration_string} at {ops_per_s:.2f} records/sec")
logger.info(f"Writing {len(movies)} records for year {year} to file {output_file}")
with open(output_file, 'w') as json_file:
    json.dump(movies, json_file, indent=2)
