"""Provide the EMOJI class."""
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

    def remove(self):
        """Remove an emoji from this subreddit.

        To remove ``'cake'`` as an emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['cake'].remove()

        """
        try:
            url = API_PATH['emoji_delete'].format(
                subreddit=self.subreddit, emoji_name=self.name)
            self._reddit.request('DELETE', url)
        except Redirect:
            pass
