"""Provide the Redditor class."""
from json import dumps

from ...const import API_PATH
from ..listing.mixins import RedditorListingMixin
from ..util import stream_generator
from .base import RedditBase
from .mixins import MessageableMixin


class Redditor(RedditBase, MessageableMixin, RedditorListingMixin):
    """A class representing the users of reddit."""

    STR_FIELD = 'name'

    @classmethod
    def from_data(cls, reddit, data):
        """Return an instance of Redditor, or None from ``data``."""
        if data == '[deleted]':
            return None
        return cls(reddit, data)

    @property
    def stream(self):
        """Provide an instance of :class:`.RedditorStream`.

        Streams can be used to indefinitely retrieve new comments made by a
        redditor, like:

        .. code:: python

           for comment in reddit.redditor('spez').stream.comments():
               print(comment)

        Additionally, new submissions can be retrieved via the stream. In the
        following example all submissions are fetched via the redditor
        ``spez``:

        .. code:: python

           for submission in reddit.redditor('spez').stream.submissions():
               print(submission)

        """
        if self._stream is None:
            self._stream = RedditorStream(self)
        return self._stream

    def __init__(self, reddit, name=None, _data=None):
        """Initialize a Redditor instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param name: The name of the redditor.

        """
        if bool(name) == bool(_data):
            raise TypeError('Either `name` or `_data` must be provided.')
        super(Redditor, self).__init__(reddit, _data)
        self._listing_use_sort = True
        if name:
            self.name = name
        self._path = API_PATH['user'].format(user=self)
        self._stream = None

    def _info_path(self):
        return API_PATH['user_about'].format(user=self)

    def _friend(self, method, data):
        url = API_PATH['friend_v1'].format(user=self)
        self._reddit.request(method, url, data=dumps(data))

    def block(self):
        """Block the Redditor."""
        self._reddit.post(API_PATH['block_user'],
                          params={'account_id': self.fullname})

    def friend(self, note=None):
        """Friend the Redditor.

        :param note: A note to save along with the relationship. Requires
            reddit Gold (default: None).

        Calling this method subsequent times will update the note.

        """
        self._friend('PUT', data={'note': note} if note else {})

    def friend_info(self):
        """Return a Redditor instance with specific friend-related attributes.

        :returns: A :class:`.Redditor` instance with fields ``date``, ``id``,
            and possibly ``note`` if the authenticated user has reddit Gold.

        """
        return self._reddit.get(API_PATH['friend_v1'].format(user=self))

    def gild(self, months=1):
        """Gild the Redditor.

        :param months: Specifies the number of months to gild up to 36
            (default: 1).

        """
        if months < 1 or months > 36:
            raise TypeError('months must be between 1 and 36')
        self._reddit.post(API_PATH['gild_user'].format(username=self),
                          data={'months': months})

    def multireddits(self):
        """Return a list of the redditor's public multireddits."""
        return self._reddit.get(API_PATH['multireddit_user'].format(user=self))

    def unblock(self):
        """Unblock the Redditor."""
        data = {'container': self._reddit.user.me().fullname,
                'name': str(self), 'type': 'enemy'}
        url = API_PATH['unfriend'].format(subreddit='all')
        self._reddit.post(url, data=data)

    def unfriend(self):
        """Unfriend the Redditor."""
        self._friend(method='DELETE', data={'id': str(self)})


class RedditorStream(object):
    """Provides submission and comment streams."""

    def __init__(self, redditor):
        """Create a RedditorStream instance.

        :param redditor: The redditor associated with the streams.

        """
        self.redditor = redditor

    def comments(self, **stream_options):
        """Yield new comments as they become available.

        Comments are yielded oldest first. Up to 100 historical comments will
        initially be returned.

        Keyword arguments are passed to :meth:`.stream_generator`.

        For example, to retrieve all new comments made by redditor ``spez``,
        try:

        .. code:: python

           for comment in reddit.redditor('spez').stream.comments():
               print(comment)

        """
        return stream_generator(self.redditor.comments.new, **stream_options)

    def submissions(self, **stream_options):
        """Yield new submissions as they become available.

        Submissions are yielded oldest first. Up to 100 historical submissions
        will initially be returned.

        Keyword arguments are passed to :meth:`.stream_generator`.

        For example to retrieve all new submissions made by redditor
        ``spez``, try:

        .. code:: python

           for submission in reddit.redditor('spez').stream.submissions():
               print(submission)

        """
        return stream_generator(self.redditor.submissions.new,
                                **stream_options)
