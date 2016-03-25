"""Provide the Redditor class."""
from json import dumps

from ...const import API_PATH
from ..listing.mixins import RedditorListingMixin
from .base import RedditBase
from .mixins import GildableMixin, MessageableMixin


class Redditor(RedditBase, GildableMixin, MessageableMixin,
               RedditorListingMixin):
    """A class representing the users of reddit."""

    EQ_FIELD = 'name'

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

    def friend(self, note=None, _unfriend=False):
        """Friend the user.

        :param note: A personal note about the user. Requires reddit Gold.
        :param _unfriend: Unfriend the user. Please use :meth:`unfriend`
            instead of setting this parameter manually.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['friend_v1'].format(user=self.name)
        # This endpoint wants the data to be a string instead of an actual
        # dictionary, although it is not required to have any content for adds.
        # Unfriending does require the 'id' key.
        if _unfriend:
            data = {'id': self.name}
        else:
            # We cannot send a null or empty note string.
            data = {'note': note} if note else {}
        method = 'DELETE' if _unfriend else 'PUT'
        return self.reddit_session.request_json(url, data=dumps(data),
                                                method=method)

    def get_blocked(self):
        """Return a UserList of Redditors with whom the user has blocked."""
        url = self.reddit_session.config['blocked']
        return self.reddit_session.request_json(url)

    def get_friend_info(self):
        """Return information about this friend, including personal notes.

        The personal note can be added or overwritten with :meth:friend, but
            only if the user has reddit Gold.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['friend_v1'].format(user=self.name)
        data = {'id': self.name}
        return self.reddit_session.request_json(url, data=data, method='GET')

    def unfriend(self):
        """Unfriend the user.

        :returns: The json response from the server.

        """
        return self.friend(_unfriend=True)
