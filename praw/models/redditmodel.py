"""Provide the RedditModel class."""
from six import PY3, iteritems

from ..const import API_PATH


class RedditModel(object):
    """Base class that represents actual Reddit objects."""

    REDDITOR_KEYS = ('approved_by', 'author', 'banned_by', 'redditor',
                     'revision_by')

    @classmethod
    def from_api_response(cls, reddit, json_dict):
        """Return an instance of the appropriate class from the json_dict."""
        return cls(reddit, json_dict=json_dict)

    def __init__(self, reddit, json_dict=None, fetch=True, info_path=None,
                 underscore_names=None, uniq=None):
        """Create a new object from the dict of attributes returned by the API.

        The fetch parameter specifies whether to retrieve the object's
        information from the API (only matters when it isn't provided using
        json_dict).

        """
        self._info_path = info_path or API_PATH['info']
        self._reddit = reddit
        self._underscore_names = underscore_names
        self._uniq = uniq
        self._has_fetched = self._populate(json_dict, fetch)

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        return (isinstance(other, RedditModel) and
                self.fullname == other.fullname)

    def __hash__(self):
        """Return the hash of the current instance."""
        return hash(self.fullname)

    def __getattr__(self, attr):
        """Return the value of the `attr` attribute."""
        if attr != '__setstate__' and not self._has_fetched:
            self._has_fetched = self._populate(None, True)
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
            subreddit = Subreddit(self._reddit, value, fetch=False)
            object.__setattr__(self, name, subreddit)
            return
        elif value and name in self.REDDITOR_KEYS:
            if isinstance(value, bool):
                pass
            elif isinstance(value, dict):
                value = Redditor(self._reddit, json_dict=value['data'])
            elif not value or value == '[deleted]':
                value = None
            else:
                value = Redditor(self._reddit, value, fetch=False)
        object.__setattr__(self, name, value)

    def __str__(self):
        """Return a string representation of the instance."""
        retval = self.__unicode__()
        if not PY3:
            retval = retval.encode('utf-8')
        return retval

    def _get_json_dict(self):
        params = {'uniq': self._uniq} if self._uniq else {}
        response = self._reddit.request(self._info_path, params=params)
        return response['data']

    def _populate(self, json_dict, fetch):
        if json_dict is None:
            json_dict = self._get_json_dict() if fetch else {}

        if self._reddit.config.store_json_result is True:
            self.json_dict = json_dict
        else:
            self.json_dict = None

        # Wikipagelisting hack. Is this still needed?
        if isinstance(json_dict, list):
            json_dict = {'_tmp': json_dict}

        for name, value in iteritems(json_dict):
            if self._underscore_names and name in self._underscore_names:
                name = '_' + name
            setattr(self, name, value)

        self._post_populate(fetch)
        return bool(json_dict) or fetch

    def _post_populate(self, fetch):
        """Called after populating the attributes of the instance."""

    @property
    def fullname(self):
        """Return the object's fullname.

        A fullname is an object's kind mapping like `t3` followed by an
        underscore and the object's base36 id, e.g., `t1_c5s96e0`.

        """
        object_id = self.id  # pylint: disable=invalid-name
        by_object = self._reddit.config.by_object
        return '{0}_{1}'.format(by_object[self.__class__], object_id)
