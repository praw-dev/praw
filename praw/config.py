"""Provides the code to load PRAW's configuration file `praw.ini`."""
import os
import sys

from six import iteritems
from six.moves import configparser

from . import models
from .errors import ClientException


class Config(object):
    """A class containing the configuration for a reddit site."""

    CONFIG = None

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

        def fetch_or_none(key):
            if key in settings:  # Passed in values have the highest priority
                return obj[key]
            return os.getenv(key) or obj.get(key) or None

        if Config.CONFIG is None:
            self._load_config()

        obj = dict(Config.CONFIG.items(site_name), **settings)
        self.by_kind = {obj['comment_kind']:    models.Comment,
                        obj['message_kind']:    models.Message,
                        obj['redditor_kind']:   models.Redditor,
                        obj['submission_kind']: models.Submission,
                        obj['subreddit_kind']:  models.Subreddit,
                        'LabeledMulti':         models.Multireddit,
                        'modaction':            models.ModAction,
                        'more':                 models.MoreComments,
                        'wikipage':             models.WikiPage,
                        'wikipagelisting':      models.WikiPageList,
                        'UserList':             models.UserList}
        self.by_object = dict((value, key) for (key, value) in
                              iteritems(self.by_kind))

        self._short_url = obj.get('short_url') or None
        self.check_for_updates = config_boolean(
            fetch_or_none('check_for_updates'))
        self.client_id = fetch_or_none('client_id')
        self.client_secret = fetch_or_none('client_secret')
        self.http_proxy = fetch_or_none('http_proxy')
        self.https_proxy = fetch_or_none('https_proxy')
        self.log_requests = int(obj['log_requests'])
        self.oauth_url = obj['oauth_url']
        self.reddit_url = obj['reddit_url']
        self.redirect_uri = fetch_or_none('redirect_uri')
        self.refresh_token = fetch_or_none('refresh_token')
        self.password = fetch_or_none('password')
        self.store_response_data = config_boolean(obj['store_response_data'])
        self.timeout = float(obj['timeout'])
        self.user_agent = fetch_or_none('user_agent')
        self.username = fetch_or_none('username')
        self.validate_certs = config_boolean(obj['validate_certificates'])

    @property
    def short_url(self):
        """Return the short url or raise a ClientException when not set."""
        if self._short_url is None:
            raise ClientException('No short domain specified.')
        return self._short_url
