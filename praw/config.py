"""Provides the code to load PRAW's configuration file `praw.ini`."""
import os
import sys

from six import iteritems
from six.moves import configparser
from six.moves.urllib.parse import urljoin

from . import models
from .const import API_PATHS
from .errors import ClientException


class Config(object):
    """A class containing the configuration for a reddit site."""

    def __init__(self, site_name, **kwargs):
        """Initialize PRAW's configuration."""
        def config_boolean(item):
            return item and item.lower() in ('1', 'yes', 'true', 'on')

        obj = dict(CONFIG.items(site_name))
        # Overwrite configuration file settings with those given during
        # instantiation of the Reddit instance.
        for key, value in kwargs.items():
            obj[key] = value

        self.by_kind = {obj['comment_kind']:    models.Comment,
                        obj['message_kind']:    models.Message,
                        obj['redditor_kind']:   models.Redditor,
                        obj['submission_kind']: models.Submission,
                        obj['subreddit_kind']:  models.Subreddit,
                        'LabeledMulti':         models.Multireddit,
                        'modaction':            models.ModAction,
                        'more':                 models.MoreComments,
                        'wikipage':             models.WikiPage,
                        'wikipagelisting':      models.WikiPageListing,
                        'UserList':             models.UserList}
        self.by_object = dict((value, key) for (key, value) in
                              iteritems(self.by_kind))
        self.by_object[models.Redditor] = obj['redditor_kind']
        self.check_for_updates = config_boolean(obj['check_for_updates'])
        self.log_requests = int(obj['log_requests'])
        # `get(...) or None` is used because `get` may return an empty string
        self.http_proxy = (os.getenv('http_proxy') or obj.get('http_proxy') or
                           None)
        self.https_proxy = (os.getenv('https_proxy') or
                            obj.get('https_proxy') or None)
        self.client_id = obj.get('oauth_client_id') or None
        self.client_secret = obj.get('oauth_client_secret') or None
        self.redirect_uri = obj.get('oauth_redirect_uri') or None
        self.refresh_token = obj.get('oauth_refresh_token') or None
        self.oauth_url = obj['oauth_url']
        self.reddit_url = obj['reddit_url']
        self._short_url = obj.get('short_url') or None
        self.store_json_result = config_boolean(obj.get('store_json_result'))
        self.timeout = float(obj['timeout'])
        self.validate_certs = config_boolean(obj.get('validate_certs'))

    def __getitem__(self, key):
        """Return the URL for key."""
        return urljoin(self.oauth_url, API_PATHS[key])

    @property
    def short_url(self):
        """Return the short url or raise a ClientException when not set."""
        if self._short_url is None:
            raise ClientException('No short domain specified.')
        return self._short_url


def _load_configuration():
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
    if not config.read(locations):
        raise Exception('Could not find config file in any of: {0}'
                        .format(locations))
    return config
CONFIG = _load_configuration()
del _load_configuration
