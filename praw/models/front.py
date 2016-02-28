"""Provide the Subreddit class."""
from .mixins import Listing


class Front(Listing):
    def __init__(self, reddit):
        super(Front, self).__init__(reddit)
        self._url = self._reddit.config.oauth_url
