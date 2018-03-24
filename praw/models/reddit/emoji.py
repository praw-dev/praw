"""Provide the Emoji class."""
import os

from ...const import API_PATH
from .base import RedditBase


class Emoji(RedditBase):
    """An individual Emoji object."""

    __hash__ = RedditBase.__hash__
    STR_FIELD = 'name'

    def __init__(self, reddit, subreddit, name, _data=None, emoji_set='subreddit'):
        """Construct an instance of the Emoji object."""
        self.subreddit = subreddit
        self.name = name
        self.emoji_set = emoji_set
        if _data is not None:
            self.url = _data['url']
            self.created_by = _data['created_by']
        else:
            self.url = None
            self.created_by = None
        super(Emoji, self).__init__(reddit, _data)

    def add(self, filepath):
        """Add an emoji to this subreddit by Emoji.

        :param filepath: Path to the file being added.
        :returns: The Emoji added.

        To add ``'test'`` to the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['test'].add('test.png')

        """
        self.subreddit.emoji.add(self.name,filepath)

    def remove(self):
        """Remove an emoji from this subreddit by Emoji.

        To remove ``'test'`` as an emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['test'].remove()

        """
        emoji_remove = self.subreddit.emoji[self.name]
        if emoji_remove is not None:
            url = API_PATH['emoji_delete'].format(
                subreddit=self.subreddit, emoji_name=self.name)
            self._reddit.request('DELETE', url)


class SubredditEmoji(RedditBase):
    """Provides a set of functions to a Subreddit for emoji."""

    __hash__ = RedditBase.__hash__

    def __call__(self, use_cached=True):
        """Return a list of Emoji for the subreddit.

        :param use_cached: If False refresh the list

        This method is to be used to discover all emoji for a subreddit:

        .. code:: python

           for emoji in reddit.subreddit('praw_test').emoji():
               print(emoji)

        """
        if not use_cached:
            self._refresh_emoji()
        return(self.emoji_subreddit)

    def __getitem__(self, name):
        """Lazily return the Emoji for the subreddit named ``name``.

        :param name: The name of the emoji
        :param use_cached: If False refresh the list

        This method is to be used to fetch a specific emoji url, like so:

        .. code:: python

           emoji = reddit.subreddit('praw_test').emoji['test']
           print(emoji)

        """
        e = self._get_emoji(name,self.emoji_subreddit)
        if e is None:
            e = self._get_emoji(name,self.emoji_default)
        if e is None:
            self._refresh_emoji()
            e = self._get_emoji(name,self.emoji_subreddit)
        return e

    def __init__(self, subreddit):
        """Create a SubredditEmoji instance.

        :param subreddit: The subreddit whose emoji are affected.

        """
        self.subreddit = subreddit
        super(SubredditEmoji, self).__init__(subreddit._reddit, None)
        self.emoji_default = []
        self.emoji_subreddit = []
        self._refresh_emoji()

    def add(self, name, filepath, use_cached=True, force_upload=True):
        """Add an emoji to this subreddit.

        :param name: The name of the emoji
        :param filepath: Path to the file being added
        :param use_cached: If False refresh the list
        :param force_upload: If False don't replace
        :returns: The Emoji added.

        To add ``'test'`` to the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji.add('test','test.png')

        """
        if not use_cached:
            self._refresh_emoji()
        if self.subreddit.emoji[name] is not None:
            if self.subreddit.emoji[name].emoji_set == 'default':
                return None
            if force_upload == False:
                return None
        self._refresh_emoji()
        filepath = filepath.strip()
        filebasename = os.path.basename(filepath)
        data = {'filepath': filebasename, 'mimetype': 'image/jpeg'}
        if filebasename.lower().endswith('.png'):
            data['mimetype'] = 'image/png'
        url = API_PATH['emoji_lease'].format(subreddit=self.subreddit)
        # until we learn otherwise, assume this request always succeeds
        s3_lease = self._reddit.post(url, data=data)['s3UploadLease']
        s3_url = 'https:' + s3_lease['action']
        # get a raw requests.Session to contact non-reddit domain
        http = self._reddit._core._requestor._http
        s3_data = {item['name']: item['value'] for item in s3_lease['fields']}
        with open(filepath, 'rb') as fp:
            response = http.post(s3_url, data=s3_data, files={'file': fp})
            response.raise_for_status()
        data = {'name': name, 's3_key': s3_data['key']}
        # assign uploaded file to subreddit
        url = API_PATH['emoji_upload'].format(
            subreddit=self.subreddit)
        self._reddit.post(url, data=data)
        return Emoji(self._reddit, self.subreddit, name)

    def remove(self, name, use_cached=True):
        """Remove an emoji from this subreddit by name.

        :param name: The name of the emoji
        :param use_cached: If False refresh the list

        To remove ``'test'`` as an emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji.remove('test')

        """
        if not use_cached:
            self._refresh_emoji()
        emoji_remove = Emoji(self._reddit, self.subreddit, name)
        self._refresh_emoji()
        emoji_remove.remove()

    def _refresh_emoji(self):
        """Fetch the current emoji for the subreddit. Not meant for endusers.

        To refresh emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji._refresh_emoji()

        """
        self.emoji_subreddit = []
        response = self.subreddit._reddit.get(
            API_PATH['emoji_list'].format(subreddit=self.subreddit))
        for emoji_name, emoji_data in \
                response[self.subreddit.fullname].items():
            emoji_cur = Emoji(self._reddit, self.subreddit,
                              emoji_name, _data=emoji_data)
            self.emoji_subreddit.append(emoji_cur)
        if self.emoji_default == []:
            for emoji_name, emoji_data in response['snoomojis'].items():
                emoji_cur = Emoji(self._reddit, self.subreddit, emoji_name,
                                  _data=emoji_data, emoji_set='default')
                self.emoji_default.append(emoji_cur)

    def _get_emoji(self, name, emoji_set):
        """Fetch emoji helper function. Not meant for endusers.

        :param name: The name of the emoji
        :param emoji_set: Either emoji_subreddit or emoji_default

        To refresh emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji.
               _get_emoji('test',self.emoji_subreddit)

        """
        for e in emoji_set:
            if e.name == name:
                return e
        return None
