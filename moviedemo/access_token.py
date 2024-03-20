##
##

import os
import configparser
from configparser import SectionProxy
from pathlib import Path


class AccessToken(object):

    def __init__(self, file_name: str, profile: str = None):
        self.home_dir = Path.home()
        self.config_file = os.path.join(self.home_dir, file_name)
        self.profile = profile if profile else 'default'
        self.config_data = configparser.ConfigParser()
        self._token = None
        self._api_key = None

        self.read_config(self.profile)

    def read_config(self, profile: str):
        profile_config = self.read_config_file(profile)
        self._token = profile_config.get('access_token')
        self._api_key = profile_config.get('api_key')

    def read_config_file(self, profile: str) -> SectionProxy:
        try:
            self.config_data.read(self.config_file)
            return self.config_data[profile]
        except KeyError:
            raise RuntimeError(f"profile {self.profile} does not exist in config file {self.config_file}")
        except Exception as err:
            raise RuntimeError(f"can not read config file {self.config_file}: {err}")

    @property
    def token(self):
        return self._token

    @property
    def api_key(self):
        return self._api_key
