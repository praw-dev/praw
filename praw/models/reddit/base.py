"""Provide the RedditBase class."""
from six import string_types

from ...const import API_PATH, urlparse
from ...exceptions import ClientException, PRAWException
from ..base import PRAWBase


class RedditBase(PRAWBase):
    """Base class that represents actual Reddit objects."""

    REPR_FIELD = "id"
    STR_FIELD = "fullname"

    @staticmethod
    def _url_parts(url):
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ClientException("Invalid URL: {}".format(url))
        return parsed.path.rstrip("/").split("/")

    # pylint: disable=invalid-name
    @property
    def id(self):
        """Return the object's id."""
        try:
            return self._data["id"]
        except KeyError:
            if not self._fetched:
                self._fetch()
            return self._data["id"]

    @property
    def fullname(self):
        """Return the object's fullname.

        A fullname is an object's kind mapping like ``t3`` followed by an
        underscore and the object's base36 ID, e.g., ``t1_c5s96e0``.

        """
        return "{}_{}".format(self._reddit._objector.kind(self), self.id)

    @property
    def fetched(self):
        """Return True if reddit attributes have been fetched."""
        return self._fetched

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        if isinstance(other, string_types):
            return other.lower() == str(self).lower()
        return (
            isinstance(other, self.__class__)
            and str(self).lower() == str(other).lower()
        )

    def __ne__(self, other):
        """Return whether the other instance differs from the current."""
        return not self == other

    def __getattr__(self, name):
        """Return the value of attribute `name`."""
        try:
            return super(RedditBase, self).__getattr__(name)
        except AttributeError:
            pass

        if not (self._fetched or name.startswith("_")):
            self._fetch()

        return super(RedditBase, self).__getattr__(name)

    def __hash__(self):
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self).lower())

    def __init__(self, reddit, _data):
        """Initialize a RedditBase instance (or a subclass).

        :param reddit: An instance of :class:`~.Reddit`.

        """
        super(RedditBase, self).__init__(reddit, _data=_data)
        self._fetched = False
        self._info_params = {}

    def __repr__(self):
        """Return a representation of the instance."""
        return "<{}({}={!r})>".format(
            self.__class__.__name__,
            self.REPR_FIELD,
            getattr(self, self.REPR_FIELD),
        )

    def __str__(self):
        """Return a string representation of the instance."""
        return getattr(self, self.STR_FIELD)

    def _fetch(self):
        if hasattr(self, "_info_path"):
            other = self._reddit.get(
                self._info_path(), params=self._info_params
            )
        else:
            self._info_params["id"] = self.fullname
            children = self._reddit.get(
                API_PATH["info"], params=self._info_params
            )._data["children"]
            if not children:
                raise PRAWException(
                    "No {!r} data returned for thing {}".format(
                        self.__class__.__name__, self.fullname
                    )
                )
            other = children[0]
        self._data.update(other._data)
        self._fetched = True

    def _reset_attributes(self, *attributes):
        for attribute in attributes:
            if attribute in self._data:
                del self._data[attribute]
        self._fetched = False

    def fetch(self, force=False):
        """Manually fetch the reddit attributes for this object."""
        if force or not self._fetched:
            self._fetch()
        return self
