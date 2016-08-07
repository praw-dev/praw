"""Provides the code to load PRAW's configuration file `praw.ini`."""
import os
import sys

from six.moves import configparser

from .exceptions import ClientException


class Config(object):
    """A class containing the configuration for a reddit site."""

    CONFIG = None
    CONFIG_NOT_SET = object()  # Represents a config value that is not set.

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

    def __init__(self, site_name, **settings):
        """Initialize a Config instance."""
        def config_boolean(item):
            return item.lower() in {'1', 'yes', 'true', 'on'}

        def fetch_or_not_set(key):
            if key in settings:  # Passed in values have the highest priority
                return raw[key]
            return os.getenv('praw_{}'.format(key)) or raw.get(key) \
                or self.CONFIG_NOT_SET

        if Config.CONFIG is None:
            self._load_config()

        raw = dict(Config.CONFIG.items(site_name), **settings)

        self._short_url = raw.get('short_url') or self.CONFIG_NOT_SET
        self.check_for_updates = config_boolean(
            fetch_or_not_set('check_for_updates'))
        self.client_id = fetch_or_not_set('client_id')
        self.client_secret = fetch_or_not_set('client_secret')
        self.http_proxy = fetch_or_not_set('http_proxy')
        self.https_proxy = fetch_or_not_set('https_proxy')
        self.kinds = {x: raw['{}_kind'.format(x)] for x in
                      ['comment', 'message', 'redditor', 'submission',
                       'subreddit']}
        self.oauth_url = raw['oauth_url']
        self.reddit_url = raw['reddit_url']
        self.redirect_uri = fetch_or_not_set('redirect_uri')
        self.refresh_token = fetch_or_not_set('refresh_token')
        self.password = fetch_or_not_set('password')
        self.user_agent = fetch_or_not_set('user_agent')
        self.username = fetch_or_not_set('username')

    @property
    def short_url(self):
        """Return the short url or raise a ClientException when not set."""
        if self._short_url is self.CONFIG_NOT_SET:
            raise ClientException('No short domain specified.')
        return self._short_url
