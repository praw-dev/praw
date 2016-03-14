"""Provide the RedditModel class."""
from six import PY3

from ..base import PRAWBase


class RedditBase(PRAWBase):
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

    def __init__(self, reddit, _data):
        """Initialize a RedditBase instance.

        :param reddit: An instance of :class:`~.Reddit`.

        """
        super(RedditBase, self).__init__(reddit, _data)
        self._fetched = False

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        return (isinstance(other, RedditBase) and
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

    def __str__(self):
        """Return a string representation of the instance."""
        retval = self.__unicode__()
        if not PY3:
            retval = retval.encode('utf-8')
        return retval

    def _fetch(self):
        other = self._reddit.request(self._info_path())
        self.__dict__.update(other.__dict__)
        self._fetched = True
