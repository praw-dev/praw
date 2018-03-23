"""Provide the Emoji class."""
from prawcore import Redirect

from ...const import API_PATH
from .base import RedditBase


class Emoji(RedditBase):
    """An individual Emoji object."""

    __hash__ = RedditBase.__hash__
    STR_FIELD = 'name'

    def __init__(self, reddit, subreddit, name, _data=None):
        """Construct an instance of the Emoji object."""
        self.reddit = reddit
        self.subreddit = subreddit
        self.name = name
        super(Emoji, self).__init__(reddit, _data)
