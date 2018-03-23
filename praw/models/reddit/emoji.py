"""Provide the Emoji class."""
import os

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

    def add(self, filepath):
        """Add an emoji to this subreddit by Emoji.

        :param filepath: Path to the file being added.
        :returns: The Emoji added.

        To add ``'cake'`` to the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['cake'].add('cake.png')

        """
        filepath = filepath.strip()
        filebasename = os.path.basename(filepath)
        data = {'filepath': filebasename, 'mimetype': 'image/jpeg'}
        if filebasename.lower().endswith('.png'):
            data['mimetype'] = 'image/png'
        url = API_PATH['emoji_lease'].format(subreddit=self.subreddit)
        # until we learn otherwise, assume this request always succeeds
        s3_lease = self.reddit.post(url, data=data)['s3UploadLease']
        s3_url = 'https:' + s3_lease['action']
        # get a raw requests.Session to contact non-reddit domain
        http = self.reddit._core._requestor._http
        s3_data = {item['name']: item['value'] for item in s3_lease['fields']}
        with open(filepath, 'rb') as fp:
            response = http.post(s3_url, data=s3_data, files={'file': fp})
            response.raise_for_status()
        data = {'name': self.name, 's3_key': s3_data['key']}
        # assign uploaded file to subreddit
        url = API_PATH['emoji_upload'].format(
            subreddit=self.subreddit)
        self.reddit.post(url, data=data)
        return Emoji(self.reddit, self.subreddit, self.name)

    def remove(self):
        """Remove an emoji from this subreddit by Emoji.

        To remove ``'cake'`` as an emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['cake'].remove()

        """
        emoji_remove = self.subreddit.emoji[self.name]
        if emoji_remove is not None:
            url = API_PATH['emoji_delete'].format(
                subreddit=self.subreddit, emoji_name=self.name)
            self._reddit.request('DELETE', url)


class SubredditEmoji(object):
    """Provides a set of functions to a Subreddit for emoji."""

    def __call__(self, use_cached=True):
        """Return a list of Emoji for the subreddit.

        :param use_cached: If False, refresh the list.

        This method is to be used to discover all emoji for a subreddit:

        .. code:: python

           for emoji in reddit.subreddit('praw_test').emoji():
               print(emoji)

        """
        if not use_cached:
            self.refresh_emoji()
        return(self.emoji_list)

    def __getitem__(self, name, use_cached=True):
        """Lazily return the Emoji for the subreddit named ``name``.

        :param name: The name of the emoji
        :param use_cached: If False, refresh the list.

        This method is to be used to fetch a specific emoji url, like so:

        .. code:: python

           emoji = reddit.subreddit('iama').emoji['cake']
           print(emoji)

        """
        if not use_cached:
            self.refresh_emoji()
        e = self.get_emoji(name)
        if e is None and use_cached:
            self.refresh_emoji()
            e = self.get_emoji(name)
        return e

    def __init__(self, subreddit):
        """Create a SubredditEmoji instance.

        :param subreddit: The subreddit whose emoji are affected.

        """
        self.subreddit = subreddit
        self.reddit = self.subreddit._reddit
        self.emoji_list = []
        self.refresh_emoji()

    def add(self, name, filepath, use_cached=True):
        """Add an emoji to this subreddit.

        :param name: The name of the emoji
        :param filepath: Path to the file being added.
        :param use_cached: If False, refresh the list.
        :returns: The Emoji added.

        To add ``'cake'`` to the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji.add('cake','cake.png')

        """
        if not use_cached:
            self.refresh_emoji()
        emoji_add = Emoji(self.reddit, self.subreddit, name)
        emoji_add.add(filepath)
        return(emoji_add)

    def remove(self, name, use_cached=True):
        """Remove an emoji from this subreddit by name.

        :param name: The name of the emoji
        :param use_cached: If False, refresh the list.

        To remove ``'cake'`` as an emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji.remove('cake')

        """
        if not use_cached:
            self.refresh_emoji()
        emoji_remove = Emoji(self.reddit, self.subreddit, name)
        emoji_remove.remove()

    def refresh_emoji(self):
        """Fetch the current emoji for the subreddit. Not meant for endusers.

        To refresh emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji.refresh()

        """
        self.emoji_list = []
        response = self.subreddit._reddit.get(
            API_PATH['emoji_list'].format(subreddit=self.subreddit))
        for emoji_name, emoji_data in \
                response[self.subreddit.fullname].items():
            emoji_cur = Emoji(self.subreddit._reddit,
                              self.subreddit, emoji_name, _data=emoji_data)
            self.emoji_list.append(emoji_cur)

      def get_emoji(self, name):
        """Helper functiomn to get an emoji. Not meant for endusers.

        :param name: The name of the emoji

        To refresh emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji.get_emoji('cake')

        """
        for e in self.emoji_list:
            if e.name == name:
                return e
        return None
