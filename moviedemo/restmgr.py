##
##

import datetime
import calendar
import os
import logging
import json
import requests
import warnings
import base64
import asyncio
import ssl
from typing import Union, List
from requests.adapters import HTTPAdapter, Retry
from requests.auth import AuthBase
from aiohttp import ClientSession, TCPConnector
from moviedemo.access_token import AccessToken
from moviedemo.retry import retry
if os.name == 'nt':
    import certifi_win32
    certifi_where = certifi_win32.wincerts.where()
else:
    import certifi
    certifi_where = certifi.where()

logger = logging.getLogger('restmgr')
logger.addHandler(logging.NullHandler())
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)


class BearerAuth(AuthBase):

    def __init__(self, key_id: str, token: str):
        self.profile_key_id = key_id
        self.profile_token = token

        self.request_headers = {
            "Authorization": f"Bearer {self.profile_token}",
        }

    def __call__(self, r):
        r.headers.update(self.request_headers)
        return r

    def get_header(self):
        return self.request_headers


class BasicAuth(AuthBase):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        auth_hash = f"{self.username}:{self.password}"
        auth_bytes = auth_hash.encode('ascii')
        auth_encoded = base64.b64encode(auth_bytes)

        self.request_headers = {
            "Authorization": f"Basic {auth_encoded.decode('ascii')}",
        }

    def __call__(self, r):
        r.headers.update(self.request_headers)
        return r

    def get_header(self):
        return self.request_headers


class RESTManager(object):

    def __init__(self,
                 hostname: Union[str, None] = None,
                 username: Union[str, None] = None,
                 password: Union[str, None] = None,
                 token_file: Union[str, None] = None,
                 use_ssl: bool = True,
                 verify: bool = True,
                 port: Union[int, None] = None,
                 profile: Union[str, None] = None):
        warnings.filterwarnings("ignore")
        self.hostname = hostname
        self.username = username
        self.password = password
        self.token_file = token_file
        self.auth_class = None
        self.profile = profile
        self.ssl = use_ssl
        self.verify = verify
        self.port = port
        self.scheme = 'https' if self.ssl else 'http'
        self.response_text = None
        self.response_list = []
        self.response_dict = {}
        self.response_code = 200
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        self.ssl_context = ssl.create_default_context()
        self.ssl_context.load_verify_locations(certifi_where)

        if self.username is not None and self.password is not None:
            self.auth_class = BasicAuth(self.username, self.password)
        elif self.token_file is not None:
            access = AccessToken(self.token_file, self.profile)
            logger.debug(f"Using key: {access.api_key}")
            self.auth_class = BearerAuth(access.api_key, access.token)

        if self.auth_class:
            self.request_headers = self.auth_class.get_header()
        else:
            self.request_headers = {}
        self.session = requests.Session()
        retries = Retry(total=10,
                        backoff_factor=0.01)
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        if not port:
            if use_ssl:
                self.port = 443
            else:
                self.port = 80

        self.url_prefix = f"{self.scheme}://{self.hostname}:{self.port}"

    def get(self, url: str):
        response = self.session.get(url, auth=self.auth_class, verify=self.verify)
        self.response_text = response.text
        self.response_code = response.status_code
        return self

    def post(self, url: str, body: dict):
        response = self.session.post(url, auth=self.auth_class, json=body, verify=self.verify)
        self.response_text = response.text
        self.response_code = response.status_code
        return self

    def patch(self, url: str, body: dict):
        response = self.session.patch(url, auth=self.auth_class, json=body, verify=self.verify)
        self.response_text = response.text
        self.response_code = response.status_code
        return self

    def put(self, url: str, body: dict):
        response = self.session.put(url, auth=self.auth_class, json=body, verify=self.verify)
        self.response_text = response.text
        self.response_code = response.status_code
        return self

    def delete(self, url: str):
        response = self.session.delete(url, auth=self.auth_class, verify=self.verify)
        self.response_text = response.text
        self.response_code = response.status_code
        return self

    def validate(self):
        if self.response_code >= 300:
            raise RuntimeError(self.response_text)
        return self

    def json(self):
        try:
            return json.loads(self.response_text)
        except json.decoder.JSONDecodeError:
            return {}

    def as_json(self):
        try:
            self.response_dict = json.loads(self.response_text)
        except json.decoder.JSONDecodeError:
            self.response_dict = {}
        return self

    def list(self):
        return self.response_list

    def filter(self, key: str, value: str):
        self.response_list = [item for item in self.response_list if item.get(key) == value]
        return self

    def default(self):
        try:
            self.response_dict = self.response_list[0]
        except IndexError:
            self.response_dict = {}
        return self

    def item(self, index: int):
        try:
            self.response_dict = self.response_list[index]
        except IndexError:
            self.response_dict = {}
        return self

    def key(self, key: str):
        return self.response_dict.get(key)

    def record(self):
        if self.response_dict:
            return self.response_dict
        else:
            return None

    def unique(self):
        if len(self.response_list) > 1:
            raise ValueError("More than one object matches search criteria")
        return self.default()

    def page_url(self, endpoint: str, page: int) -> str:
        return f"{self.url_prefix}{endpoint}&page={page}"

    def build_url(self, endpoint: str) -> str:
        return f"{self.url_prefix}{endpoint}"

    @retry()
    async def get_async(self, url: str):
        conn = TCPConnector(ssl_context=self.ssl_context)
        async with ClientSession(headers=self.request_headers, connector=conn) as session:
            async with session.get(url, verify_ssl=self.verify) as response:
                if response.status == 429:
                    raise RuntimeError("Too many requests")
                response = await response.json()
                return response.get('results', [])

    @retry()
    async def get_async_dict(self, url: str):
        conn = TCPConnector(ssl_context=self.ssl_context)
        async with ClientSession(headers=self.request_headers, connector=conn) as session:
            async with session.get(url, verify_ssl=self.verify) as response:
                if response.status == 429:
                    raise RuntimeError("Too many requests")
                response = await response.json()
                return response

    async def get_tmdb_a(self, endpoint: str):
        data = []
        url = self.page_url(endpoint, 1)
        logger.debug(f"Get {url}")
        cursor = self.get(url).validate().json()

        total_pages = cursor.get('total_pages', 0)
        logger.debug(f"Total pages: {total_pages}")

        for result in asyncio.as_completed([self.get_async(self.page_url(endpoint, page)) for page in range(1, total_pages + 1)]):
            block = await result
            data.extend(block)

        self.response_list = data

    async def get_tmdb_details_a(self, movies: List[dict]):
        data = []
        for i in range(0, len(movies), 100):
            sub_list = movies[i:i + 100]
            url_list = []
            for movie in sub_list:
                movie_id = movie.get('id')
                endpoint = f"/3/movie/{movie_id}"
                url = self.build_url(endpoint)
                url_list.append(url)
            for result in asyncio.as_completed([self.get_async_dict(url) for url in url_list]):
                block = await result
                if block['imdb_id'] is None or block['poster_path'] is None:
                    continue
                poster_part = block['poster_path']
                backdrop_part = block['backdrop_path']
                block['poster_path'] = f"https://image.tmdb.org/t/p/original{poster_part}"
                block['backdrop_path'] = f"https://image.tmdb.org/t/p/original{backdrop_part}"
                data.append(block)
        self.response_list = data

    def get_tmdb(self, endpoint: str):
        self.response_list = []
        self.response_dict = {}
        self.loop.run_until_complete(self.get_tmdb_a(endpoint))
        return self

    def get_tmdb_details(self, movies: List[dict]):
        self.response_list = []
        self.response_dict = {}
        self.loop.run_until_complete(self.get_tmdb_details_a(movies))
        return self

    def get_tmdb_py_year(self, year: int):
        year_list = []
        for month in range(1, 13):
            logger.info(f"Processing month {calendar.month_name[month]}")
            _, last = calendar.monthrange(year, month)
            begin = datetime.datetime(year=year, month=month, day=1)
            begin_string = begin.strftime("%Y-%m-%d")
            end = datetime.datetime(year=year, month=month, day=last)
            end_string = end.strftime("%Y-%m-%d")

            endpoint = (f"/3/discover/movie?include_adult=false&include_video=false&language=en-US&sort_by=primary_release_date.asc&primary_release_year={year}"
                        f"&with_original_language=en&primary_release_date.gte={begin_string}&primary_release_date.lte={end_string}")

            result = self.get_tmdb(endpoint).list()
            movies = self.get_tmdb_details(result).list()
            logger.info(f"{calendar.month_name[month]} has {len(movies)} records")

            year_list.extend(movies)

        return year_list

    def get_url_content(self, url) -> bytes:
        return self.session.get(url).content
