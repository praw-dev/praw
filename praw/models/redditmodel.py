"""Provide the RedditModel class."""
from six import PY3, iteritems

from ..const import API_PATH


class RedditModel(object):
    """Base class that represents actual Reddit objects."""

    REDDITOR_KEYS = ('approved_by', 'author', 'banned_by', 'redditor',
                     'revision_by')

    @property
    def fullname(self):
        """Return the object's fullname.

        A fullname is an object's kind mapping like `t3` followed by an
        underscore and the object's base36 ID, e.g., `t1_c5s96e0`.

        """
        return '{}_{}'.format(self._reddit.config.by_object[self.__class__],
                              self.id)  # pylint: disable=invalid-name

    def __init__(self, reddit, info_path=None):
        """Initialize a RedditModel instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param info_path: The path used to fetch the object. This path is
            accessed the first time an previously unknown attribute is
            accessed.

        The fetch parameter specifies whether to retrieve the object's
        information from the API (only matters when it isn't provided using
        json_data).

        """
        self._fetched = False
        self._info_path = info_path or API_PATH['info']
        self._reddit = reddit
        self._response_data = None

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        return (isinstance(other, RedditModel) and
                self.fullname == other.fullname)

    def __hash__(self):
        """Return the hash of the current instance."""
        return hash(self.fullname)

    def __getattr__(self, attr):
        """Return the value of the `attr` attribute."""
        if attr != '__setstate__' and not self._fetched:
            self._fetch()
            return getattr(self, attr)
        msg = '\'{0}\' has no attribute \'{1}\''.format(type(self), attr)
        raise AttributeError(msg)

    def __getstate__(self):
        """Needed for `pickle`.

        Without this, pickle protocol version 0 will make HTTP requests
        upon serialization, hence slowing it down significantly.
        """
        return self.__dict__

    def __ne__(self, other):
        """Return whether the other instance differs from the current."""
        return not self == other

    def __reduce_ex__(self, _):
        """Needed for `pickle`.

        Without this, `pickle` protocol version 2 will make HTTP requests
        upon serialization, hence slowing it down significantly.
        """
        return self.__reduce__()

    def __setattr__(self, name, value):
        """Set the `name` attribute to `value."""
        from .redditor import Redditor
        from .subreddit import Subreddit

        if value and name == 'subreddit':
            subreddit = Subreddit(self._reddit, value)
            object.__setattr__(self, name, subreddit)
            return
        elif value and name in self.REDDITOR_KEYS:
            if isinstance(value, bool):
                pass
            elif isinstance(value, dict):
                value = Redditor(self._reddit, 'TODO').update(value['data'])
            elif not value or value == '[deleted]':
                value = None
            else:
                value = Redditor(self._reddit, value)
        object.__setattr__(self, name, value)

    def __str__(self):
        """Return a string representation of the instance."""
        retval = self.__unicode__()
        if not PY3:
            retval = retval.encode('utf-8')
        return retval

    def _fetch(self):
        data = self._reddit.request(self._info_path)
        if self._reddit.config.store_response_data:
            self._response_data = data

        for name, value in iteritems(self._transform_data(data)):
            setattr(self, name, value)

        self._fetched = True

    def _transform_data(self, data):  # pylint: disable=no-self-use
        return data['data']
