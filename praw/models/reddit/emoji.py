"""Provide the EMOJI class."""
from ...const import API_PATH
from ..listing.generator import ListingGenerator
from .base import RedditBase
from .redditor import Redditor


class Emoji(RedditBase):
    """An individual Emoji object."""

    __hash__ = RedditBase.__hash__

    @property
    def mod(self):
        """Provide an instance of :class:`.WikiPageModeration`."""
        if self._mod is None:
            self._mod = EmojiModeration(self)
        return self._mod

    def __init__(self, reddit, subreddit, name, revision=None, _data=None):
        """Construct an instance of the WikiPage object.

        :param revision: A specific revision ID to fetch. By default, fetches
            the most recent revision.

        """
        self.name = name
        self.subreddit = subreddit
        super(Emoji, self).__init__(reddit, _data)
        self._mod = None


class EmojiModeration(object):
    """Provides a set of moderation functions for a WikiPage."""

    def __init__(self, wikipage):
        """Create a WikiPageModeration instance.

        :param wikipage: The wikipage to moderate.

        """
        self.emoji = emoji

    def add(self, emoji_name, filepath):
        """Add an emoji to this subreddit.

        :param redditor: An emoji name (e.g., ``'cake'``) or
            :class:`~.Emoji` instance.

        To add ``'cake'`` as an editor on the wikipage ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('test').wiki['praw_test'].mod.add('cake')

        """
        data = {'filepath': filepath, 'mimetype': 'image/png'}
        url = API_PATH['emoji_lease'].format(
            subreddit=self.subreddit, method='add')
        s3_key = self.wikipage._reddit.post(url, data=data)['s3_key']
        data = {'name': emoji_name, 's3_key': s3_key}
        url = API_PATH['emoji_upload'].format(
            subreddit=self.subreddit, method='add')
        self.wikipage._reddit.post(url, data=data)

    def remove(self, emoji_name):
        """Remove an emoji from this subreddit.

        :param emoji_name: An emoji name (e.g., ``'cake'``) or
            :class:`~.Emoji` instance.

        To remove ``'cake'`` as an editor on the wikipage ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('test').wiki['praw_test'].mod.remove('cake')

        """
        url = API_PATH['emoji_delete'].format(
            subreddit=self.subreddit, emoji_name=emoji_name, method='del')
        self._reddit.post(url)  