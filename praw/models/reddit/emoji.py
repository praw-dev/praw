"""Provide the Emoji class."""
import os

from ...const import API_PATH
from ...exceptions import ClientException
from .base import RedditBase


class Emoji(RedditBase):
    """An individual Emoji object."""

    STR_FIELD = 'name'

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        if isinstance(other, str):
            return other == str(self)
        return (isinstance(other, self.__class__) and
                str(self) == str(other) and other.subreddit == self.subreddit)

    def __hash__(self):
        """Return the hash of the current instance."""
        return (hash(self.__class__.__name__) ^ hash(str(self)) ^
                hash(self.subreddit))

    def __init__(self, reddit, subreddit, name, _data=None):
        """Construct an instance of the Emoji object."""
        self.name = name
        self.subreddit = subreddit
        super(Emoji, self).__init__(reddit, _data)

    def _fetch(self):
        for emoji in self.subreddit.emoji:
            if emoji.name == self.name:
                self.__dict__.update(emoji.__dict__)
                self._fetched = True
                return
        raise ClientException('/r/{} does not have the emoji {}'
                              .format(self.subreddit, self.name))

    def delete(self):
        """Delete an emoji from this subreddit by Emoji.

        To delete ``'test'`` as an emoji on the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['test'].delete()

        """
        url = API_PATH['emoji_delete'].format(
            emoji_name=self.name, subreddit=self.subreddit)
        self._reddit.request('DELETE', url)


class SubredditEmoji(object):
    """Provides a set of functions to a Subreddit for emoji."""

    def __getitem__(self, name):
        """Lazily return the Emoji for the subreddit named ``name``.

        :param name: The name of the emoji

        This method is to be used to fetch a specific emoji url, like so:

        .. code:: python

           emoji = reddit.subreddit('praw_test').emoji['test']
           print(emoji)

        """
        return Emoji(self._reddit, self.subreddit, name)

    def __init__(self, subreddit):
        """Create a SubredditEmoji instance.

        :param subreddit: The subreddit whose emoji are affected.

        """
        self.subreddit = subreddit
        self._reddit = subreddit._reddit

    def __iter__(self):
        """Return a list of Emoji for the subreddit.

        This method is to be used to discover all emoji for a subreddit:

        .. code:: python

           for emoji in reddit.subreddit('praw_test').emoji:
               print(emoji)

        """
        response = self.subreddit._reddit.get(
            API_PATH['emoji_list'].format(subreddit=self.subreddit))
        for emoji_name, emoji_data in \
                response[self.subreddit.fullname].items():
            yield Emoji(self._reddit, self.subreddit, emoji_name,
                        _data=emoji_data)

    def add(self, name, image_path):
        """Add an emoji to this subreddit.

        :param name: The name of the emoji
        :param image_path: A path to a jpeg or png image.
        :returns: The Emoji added.

        To add ``'test'`` to the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji.add('test','test.png')

        """
        data = {'filepath': os.path.basename(image_path),
                'mimetype': 'image/jpeg'}
        if image_path.lower().endswith('.png'):
            data['mimetype'] = 'image/png'
        url = API_PATH['emoji_lease'].format(subreddit=self.subreddit)

        # until we learn otherwise, assume this request always succeeds
        upload_lease = self._reddit.post(url, data=data)['s3UploadLease']
        upload_data = {item['name']: item['value']
                       for item in upload_lease['fields']}
        upload_url = 'https:{}'.format(upload_lease['action'])

        with open(image_path, 'rb') as image:
            response = self._reddit._core._requestor._http.post(
                upload_url, data=upload_data, files={'file': image})
        response.raise_for_status()

        url = API_PATH['emoji_upload'].format(
            subreddit=self.subreddit)
        self._reddit.post(url,
                          data={'name': name, 's3_key': upload_data['key']})
        return Emoji(self._reddit, self.subreddit, name)
