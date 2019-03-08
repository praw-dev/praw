"""Provide the PRAWBase superclass."""
from copy import deepcopy
from .util import RedditAttributes


class PRAWBase(object):
    """Superclass for all models in PRAW."""

    @staticmethod
    def _safely_add_arguments(argument_dict, key, **new_arguments):
        """Replace argument_dict[key] with a deepcopy and update.

        This method is often called when new parameters need to be added to a
        request. By calling this method and adding the new or updated
        parameters we can insure we don't modify the dictionary passed in by
        the caller.

        """
        value = deepcopy(argument_dict[key]) if key in argument_dict else {}
        value.update(new_arguments)
        argument_dict[key] = value

    @classmethod
    def parse(cls, data, reddit):
        """Return an instance of ``cls`` from ``data``.

        :param data: The structured data.
        :param reddit: An instance of :class:`.Reddit`.

        """
        return cls(reddit, _data=data)

    def __init__(self, reddit, _data):
        """Initialize a PRAWModel instance.

        :param reddit: An instance of :class:`.Reddit`.

        """
        self._reddit = reddit
        self._data = {} if _data is None else _data
        self._initial_data = dict(self._data)
        # pylint: disable=invalid-name
        self._a = RedditAttributes(prawobj=self, data=self._data)

    def __getattr__(self, name):
        """Return the value of attribute `name`."""
        assert self._data is abs(self._a)

        try:
            return self._data[name]
        except KeyError:
            pass

        raise AttributeError(
            "{!r} object has no attribute {!r}".format(
                self.__class__.__name__, name
            )
        )

    def __getstate__(self):
        """Extract state to pickle."""
        return self.__dict__

    def __setstate__(self, state):
        """Restore from pickled state."""
        self.__dict__.update(state)

    @property
    def a(self):  # pylint: disable=invalid-name
        """Provide an object to access the data fetched from reddit."""
        return self._a
