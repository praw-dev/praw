"""Provide the Redditor class."""
from json import dumps

from ...const import API_PATH
from ..listing.mixins import RedditorListingMixin
from .base import RedditBase
from .mixins import MessageableMixin


class Redditor(RedditBase, MessageableMixin, RedditorListingMixin):
    """A class representing the users of reddit."""

    STR_FIELD = 'name'

    @classmethod
    def from_data(cls, reddit, data):
        """Return an instance of Redditor, bool, or None from ``data``."""
        if isinstance(data, bool):
            return data
        elif data in [None, '', '[deleted]']:
            return None
        else:
            return cls(reddit, data)

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
        self._path = API_PATH['user'].format(user=self.name)

    def _info_path(self):
        return API_PATH['user_about'].format(user=self.name)

    def _friend(self, method, data):
        url = API_PATH['friend_v1'].format(user=self.name)
        return self._reddit.request(method, url, data=dumps(data))

    def friend(self, note=None):
        """Friend the Redditor.

        :param note: A personal note about the user. Requires reddit
            Gold. (Default: None)
        :returns: The json response from the server.

        Calling this method subsequent times will update the note.

        """
        return self._friend('PUT', data={'note': note} if note else {})

    def friend_info(self):
        """Return a Redditor instance with specific friend-related attributes.

        :returns: A Redditor instance with fields ``date``, ``id``, and
            possibly ``note`` if the authenticated user has reddit Gold.

        """
        return self._reddit.get(API_PATH['friend_v1'].format(user=self.name))

    def gild(self, months=1):
        """Gild the Redditor.

        :param months: Specifies the number of months to gild up to 36
            (default: 1).

        """
        if months < 1 or months > 36:
            raise TypeError('months must be between 1 and 36')
        self._reddit.post(API_PATH['gild_user'].format(username=self),
                          data={'months': months})

    def unblock(self):
        """Unblock the Redditor.

        :returns: The json response from the server.

        Blocking must be done from a Message, Comment Reply or Submission
        Reply.

        """
        data = {'container': self._reddit.user.me().fullname,
                'name': self.name, 'type': 'enemy'}
        return self._reddit.post(API_PATH['unfriend'], data=data)

    def unfriend(self):
        """Unfriend the Redditor."""
        self._friend(method='delete', data={'id': self.name})
