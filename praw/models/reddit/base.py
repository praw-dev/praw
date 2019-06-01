"""Provide the RedditBase class."""

from ...compat import string_types, urlparse
from ...exceptions import ClientException
from ..base import PRAWBase


class RedditBase(PRAWBase):
    """Base class that represents actual Reddit objects."""

    @staticmethod
    def _url_parts(url):
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ClientException("Invalid URL: {}".format(url))
        return parsed.path.rstrip("/").split("/")

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        if isinstance(other, string_types):
            return other.lower() == str(self).lower()
        return (
            isinstance(other, self.__class__)
            and str(self).lower() == str(other).lower()
        )

    def __getattr__(self, attribute):
        """Return the value of `attribute`."""
        if not attribute.startswith("_") and not self._fetched:
            self._fetch()
            return getattr(self, attribute)
        raise AttributeError(
            "{!r} object has no attribute {!r}".format(
                self.__class__.__name__, attribute
            )
        )

    def __hash__(self):
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self).lower())

    def __init__(self, reddit, _data):
        """Initialize a RedditBase instance (or a subclass).

        :param reddit: An instance of :class:`~.Reddit`.

        """
        super(RedditBase, self).__init__(reddit, _data=_data)
        self._fetched = False

    def __repr__(self):
        """Return an object initialization representation of the instance."""
        return "{}({}={!r})".format(
            self.__class__.__name__, self.STR_FIELD, str(self)
        )

    def __str__(self):
        """Return a string representation of the instance."""
        return getattr(self, self.STR_FIELD)

    def __ne__(self, other):
        """Return whether the other instance differs from the current."""
        return not self == other

    def _fetch(self):  # pragma: no cover
        self._fetched = True

    def _reset_attributes(self, *attributes):
        for attribute in attributes:
            if attribute in self.__dict__:
                del self.__dict__[attribute]
        self._fetched = False
