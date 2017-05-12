"""Provides the code to load PRAW's configuration file `praw.ini`."""
from threading import Lock
import os
import sys

from .const import configparser
from .exceptions import ClientException


class _NotSet(object):
    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def __str__(self):
        return 'NotSet'


class Config(object):
    """A class containing the configuration for a reddit site."""

    CONFIG = None
    CONFIG_NOT_SET = _NotSet()  # Represents a config value that is not set.
    LOCK = Lock()

    @staticmethod
    def _config_boolean(item):
        if isinstance(item, bool):
            return item
        return item.lower() in {'1', 'yes', 'true', 'on'}

    @classmethod
    def _load_config(cls):
        """Attempt to load settings from various praw.ini files."""
        config = configparser.RawConfigParser()
        module_dir = os.path.dirname(sys.modules[__name__].__file__)
        if 'APPDATA' in os.environ:  # Windows
            os_config_path = os.environ['APPDATA']
        elif 'XDG_CONFIG_HOME' in os.environ:  # Modern Linux
            os_config_path = os.environ['XDG_CONFIG_HOME']
        elif 'HOME' in os.environ:  # Legacy Linux
            os_config_path = os.path.join(os.environ['HOME'], '.config')
        else:
            os_config_path = None
        locations = [os.path.join(module_dir, 'praw.ini'), 'praw.ini']
        if os_config_path is not None:
            locations.insert(1, os.path.join(os_config_path, 'praw.ini'))
        config.read(locations)
        cls.CONFIG = config

    @property
    def short_url(self):
        """Return the short url or raise a ClientException when not set."""
        if self._short_url is self.CONFIG_NOT_SET:
            raise ClientException('No short domain specified.')
        return self._short_url

    def __init__(self, site_name, **settings):
        """Initialize a Config instance."""
        with Config.LOCK:
            if Config.CONFIG is None:
                self._load_config()

        self._settings = settings
        self.custom = dict(Config.CONFIG.items(site_name), **settings)

        self.client_id = self.client_secret = self.oauth_url = None
        self.reddit_url = self.refresh_token = self.redirect_uri = None
        self.password = self.user_agent = self.username = None

        self._initialize_attributes()

    def _fetch(self, key):
        value = self.custom[key]
        del self.custom[key]
        return value

    def _fetch_default(self, key, default=None):
        if key not in self.custom:
            return default
        return self._fetch(key)

    def _fetch_or_not_set(self, key):
        if key in self._settings:  # Passed in values have the highest priority
            return self._fetch(key)

        env_value = os.getenv('praw_{}'.format(key))
        ini_value = self._fetch_default(key)  # Needed to remove from custom

        # Environment variables have higher priority than praw.ini settings
        return env_value or ini_value or self.CONFIG_NOT_SET

    def _initialize_attributes(self):
        self._short_url = self._fetch_default('short_url') \
                          or self.CONFIG_NOT_SET
        self.check_for_updates = self._config_boolean(
            self._fetch_or_not_set('check_for_updates'))
        self.kinds = {x: self._fetch('{}_kind'.format(x)) for x in
                      ['comment', 'message', 'redditor', 'submission',
                       'subreddit']}

        for attribute in ('client_id', 'client_secret', 'redirect_uri',
                          'refresh_token', 'password', 'user_agent',
                          'username'):
            setattr(self, attribute, self._fetch_or_not_set(attribute))

        for required_attribute in ('oauth_url', 'reddit_url'):
            setattr(self, required_attribute, self._fetch(required_attribute))
