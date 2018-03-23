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


class SubredditEmoji(object):
    """Provides a set of functions to a Subreddit for emoji."""

    def __getitem__(self, name):
        """Lazily return the Emoji for the subreddit named ``name``.

        This method is to be used to fetch a specific emoji url, like so:

        .. code:: python

           emoji = reddit.subreddit('iama').emoji['cake']
           print(emoji)

        """
        if e.name == name for e in self.subreddit.emoji:
            return e for e in self.subreddit.emoji if e.name == name
        else:
            return None

    def __init__(self, subreddit):
        """Create a SubredditEmoji instance.

        :param subreddit: The subreddit whose emoji are affected.
        :param reddit: The reddit instance.

        """
        self.subreddit = subreddit
        self.reddit = self.subreddit._reddit

    def __iter__(self):
        """Iterate through the Emoji for the subreddit.

        This method is to be used to discover all emoji for a subreddit:

        .. code:: python

           for emoji in reddit.subreddit('praw_test').emoji:
               print(emoji)

        """
        response = self.subreddit._reddit.get(
            API_PATH['emoji_list'].format(subreddit=self.subreddit))
        for emoji_name, emoji_data in \
                response[self.subreddit.fullname].items():
            yield Emoji(self.subreddit._reddit,
                        self.subreddit, emoji_name, _data=emoji_data)

    def add(self, name, filepath):
        """Add an emoji to this subreddit.

        :param filepath: Path to the file being added.
        :returns: The Emoji added.

        To add ``'cake'`` to the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji.add('cake','cake.png')

        """
        filepath = filepath.strip()
        filebasename = os.path.basename(filepath)
        data = {'filepath': filebasename, 'mimetype': 'image/jpeg'}
        if filebasename.lower().endswith('.png'):
            data['mimetype'] = 'image/png'
        url = API_PATH['emoji_lease'].format(
            subreddit=self.subreddit, method='add')
        # until we learn otherwise, assume this request always succeeds
        s3_lease = self.reddit.post(url, data=data)['s3UploadLease']
        s3_url = 'https:' + s3_lease['action']
        # get a raw requests.Session to contact non-reddit domain
        http = self.reddit._core._requestor._http
        s3_data = {item['name']: item['value'] for item in s3_lease['fields']}
        with open(filepath, 'rb') as fp:
            response = http.post(s3_url, data=s3_data, files={'file': fp})
            response.raise_for_status()
        data = {'name': name, 's3_key': s3_data['key']}
        # assign uploaded file to subreddit
        url = API_PATH['emoji_upload'].format(
            subreddit=self.subreddit)
        self.reddit.post(url, data=data)
        return Emoji(self.reddit, self.subreddit, name)

    def remove(self, name):
        """Remove an emoji from this subreddit.

        To remove ``'cake'`` as an emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['cake'].remove()

        """
        emoji_remove = self.subreddit.emoji[name]
        if emoji_remove is not None:
            url = API_PATH['emoji_delete'].format(
                subreddit=self.subreddit, emoji_name=name)
            self._reddit.request('DELETE', url)
