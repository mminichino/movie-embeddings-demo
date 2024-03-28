#!/usr/bin/env python3

import logging
import json
import warnings
import time
import argparse
from moviedemo.restmgr import RESTManager
from moviedemo.logformat import CustomDisplayFormatter

warnings.filterwarnings("ignore")
logger = logging.getLogger()


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--host', action='store', help="API Host Name", default="api.themoviedb.org")
    parser.add_argument('-t', '--token', action='store', help="Token", default="tmdb.key")
    parser.add_argument('-y', '--year', action='store', help="Year", type=int, default=2023)
    options = parser.parse_args()

    output_file = f"movie-data-{options.year}.json"

    screen_handler = logging.StreamHandler()
    screen_handler.setFormatter(CustomDisplayFormatter())
    logger.addHandler(screen_handler)
    logger.setLevel(logging.INFO)

    rest = RESTManager(hostname=options.host, token_file=options.token)

    start_time = time.perf_counter()
    movies = rest.get_tmdb_py_year(options.year)
    end_time = time.perf_counter()

    record_count = len(movies)
    run_duration = end_time - start_time
    duration_string = time.strftime("%H hours %M minutes %S seconds.", time.gmtime(run_duration))
    ops_per_s = record_count / run_duration
    logger.info(f"Export completed in {duration_string} at {ops_per_s:.2f} records/sec")
    logger.info(f"Writing {len(movies)} records for year {options.year} to file {output_file}")
    with open(output_file, 'w') as json_file:
        json.dump(movies, json_file, indent=2)


if __name__ == '__main__':
    main()
