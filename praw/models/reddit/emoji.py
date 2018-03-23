"""Provide the EMOJI class."""
from ...const import API_PATH
from .base import RedditBase


class Emoji(RedditBase):
    """An individual Emoji object."""

    __hash__ = RedditBase.__hash__
    STR_FIELD = 'name'

    @property
    def __init__(self, reddit, subreddit, name, _data=None):
        """Construct an instance of the Emoji object."""
        self.name = name
        self.subreddit = subreddit
        super(Emoji, self).__init__(reddit, _data)
        self._mod = None

    def add(self, filepath):
        """Add an emoji to this subreddit.

        :param emoji: An emoji name (e.g., ``'cake'``) or
            :class:`~.Emoji` instance.

        To add ``'cake'`` to the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['cake'].add('cake.png')

        """
        data = None
        if filepath[-4:].lower() == '.png':
            data = {'filepath': filepath, 'mimetype': 'image/png'}
        elif filepath[-4:].lower() == '.jpg' \
                or filepath[-4:].lower() == '.jpeg':
            data = {'filepath': filepath, 'mimetype': 'image/jpeg'}
        if data is not None:
            url = API_PATH['emoji_lease'].format(
                subreddit=self.subreddit, method='add')
            s3_key = self._reddit.post(url, data=data)['s3_key']
            data = {'name': self.name, 's3_key': s3_key}
            url = API_PATH['emoji_upload'].format(
                subreddit=self.subreddit, method='add')
            self._reddit.post(url, data=data)

    def remove(self):
        """Remove an emoji from this subreddit.

        :param emoji_name: An emoji name (e.g., ``'cake'``) or
            :class:`~.Emoji` instance.

        To remove ``'cake'`` as an emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['cake'].remove()

        """
        url = API_PATH['emoji_delete'].format(
            subreddit=self.subreddit, emoji_name=self.name, method='del')
        self._reddit.post(url)
