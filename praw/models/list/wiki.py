"""Provide the WikiPageList class."""
from ..reddit.wikipage import WikiPage
from .base import BaseList


class WikiPageList(BaseList):
    """A list of WikiPages. Works just like a regular list."""

    CHILD_ATTRIBUTE = '_tmp'

    @staticmethod
    def _convert(reddit, data):
        """Return a WikiPage object from the data."""
        subreddit = reddit._request_url.rsplit('/', 4)[1]
        return WikiPage(reddit, subreddit, data, fetch=False)
