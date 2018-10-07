"""Provide the RemovalReason class."""
from ...const import API_PATH
from .base import RedditBase


class RemovalReason(RedditBase):
    """A removal reason for a subreddit."""

    STR_FIELD = 'id'

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        if isinstance(other, str):
            return other == str(self)
        return (isinstance(other, self.__class__) and
                str(self) == str(other))

    def __hash__(self):
        """Return the hash of the current instance."""
        return hash(str(self))

    def __init__(self, reddit, subreddit,
                 id, _data=None):  # pylint: disable=redefined-builtin
        """Construct an instance of the RemovalReason object."""
        self.subreddit = subreddit
        self.id = id  # pylint: disable=invalid-name
        super(RemovalReason, self).__init__(reddit, _data)

    def _fetch(self):
        raw = self._reddit.get(
            API_PATH['removal_reasons'].format(subreddit=self.subreddit))
        try:
            self.__dict__.update(raw['data'][self.id])
        except KeyError:
            raise ClientException('/r/{} does not have the removal reason {}'
                                  .format(self.subreddit, self.id))

    def delete(self):
        """Delete a removal reason from its subreddit."""
        url = API_PATH['removal_reason_update'].format(
            id=self.id, subreddit=self.subreddit)
        self._reddit.request('DELETE', url)

    def edit(self, title, message):
        """Edit a removal reason."""
        url = API_PATH['removal_reason_update'].format(
            id=self.id, subreddit=self.subreddit)
        self._reddit.request('PUT', url, {'title': title, 'message': message})


class SubredditRemovalReasons(object):
    """Provides management functions for a subreddit's removal reasons."""

    def __getitem__(self, key):
        """Return a :class:`.RemovalReason` from this subreddit by ID or index.

        Getting by ID is lazy, but getting by index is eager.

        :param key: The ID or index of the removal reason.

        To get the first removal reason of /r/praw_test:

        .. code:: python

            subreddit = reddit.subreddit('praw_test')
            reason = subreddit.removal_reasons[0]

        To get a removal reason from /r/praw_test with the ID '11qiw1rp2mlqd':

        .. code:: python

            subreddit = reddit.subreddit('praw_test')
            reason = subreddit.removal_reasons['11qiw1rp2mlqd']

        """
        if isinstance(key, int):
            raw = self._reddit.get(
                API_PATH['removal_reasons'].format(subreddit=self.subreddit))
            reason = raw['order'][key]
            return RemovalReason(self._reddit,
                                 self.subreddit,
                                 reason,
                                 _data=raw['data'][reason])
        return RemovalReason(self._reddit, self.subreddit, key)

    def __init__(self, subreddit):
        """Create a SubredditRemovalReasons instance.

        :param subreddit: The subreddit whose removal reasons are
            affected.
        """
        self.subreddit = subreddit
        self._reddit = subreddit._reddit

    def __iter__(self):
        """Iterate over the removal reasons for this subreddit, in order."""
        raw = self._reddit.get(
            API_PATH['removal_reasons'].format(subreddit=self.subreddit))
        for reason in raw['order']:
            yield RemovalReason(self._reddit,
                                self.subreddit,
                                reason,
                                _data=raw['data'][reason])


    def add(self, title, message):
        """Add a removal reason to this subreddit.

        :param title: The title of the removal reason.
        :param message: The body of the removal reason.
        :returns: The RemovalReason added.  (Lazy)
        """
        url = API_PATH['removal_reasons'].format(subreddit=self.subreddit)
        response = self._reddit.post(url, {'title': title, 'message': message})
        return RemovalReason(self._reddit,
                             self.subreddit,
                             response['id'])
