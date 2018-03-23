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

    def add(self, filepath):
        """Add an emoji to this subreddit.

        :param emoji: An emoji name (e.g., ``'cake'``) or
            :class:`~.Emoji` instance.

        To add ``'cake'`` to the subreddit ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('praw_test').emoji['cake'].add('cake.png')

        """
        data = None
        if filepath.lower().endswith('.png'):
            data = {'filepath': filepath, 'mimetype': 'image/png'}
        elif filepath.lower().endswith('.jpg') \
                or filepath.lower().endswith('.jpeg'):
            data = {'filepath': filepath, 'mimetype': 'image/jpeg'}
        if data is not None:
            url = API_PATH['emoji_lease'].format(
                subreddit=self.subreddit, method='add')
            s3_lease = self._reddit.post(url, data=data)['s3UploadLease']
            s3_url = 'https:' + s3_lease['action']
            # get a raw requests.Session to contact non-reddit domain
            http = self.subreddit._reddit._core._requestor._http
            s3_parameters = dict((item['name'], item['value'])
                                 for item in s3_lease['fields'])
            with open(filepath, 'rb') as file:
                s3_parameters['file'] = file
                http.post(s3_url, files=s3_parameters)
            data = {'name': self.name, 's3_key': s3_parameters['key']}
            # assign uploaded file to subreddit
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
            subreddit=self.subreddit, emoji_name=self.name)
        self._reddit.request('DELETE',url)
