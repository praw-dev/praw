"""Provide the ListingGenerator class."""
from copy import deepcopy

from .listing import FlairListing
from ..base import PRAWBase


class ListingGenerator(PRAWBase):
    """Instances of this class generate :class:`.RedditBase` instances.

    .. warning:: This class should not be directly utilized. Instead you will
       find a number of methods that return instances of the class:

       http://praw.readthedocs.io/en/latest/search.html?q=ListingGenerator

    """

    def __init__(self, reddit, url, limit=100, params=None):
        """Initialize a ListingGenerator instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param url: A URL returning a reddit listing.
        :param limit: The number of content entries to fetch. If ``limit`` is
            None, then fetch as many entries as possible. Most of reddit's
            listings contain a maximum of 1000 items, and are returned 100 at a
            time. This class will automatically issue all necessary
            requests (default: 100).
        :param params: A dictionary containing additional query string
            parameters to send with the request.

        """
        super(ListingGenerator, self).__init__(reddit, _data=None)
        self._exhausted = False
        self._listing = None
        self._list_index = None
        self.limit = limit
        self.params = deepcopy(params) if params else {}
        self.params["limit"] = limit or 1024
        self.url = url
        self.yielded = 0

    def __iter__(self):
        """Permit ListingGenerator to operate as an iterator."""
        return self

    def __next__(self):
        """Permit ListingGenerator to operate as a generator in py3."""
        if self.limit is not None and self.yielded >= self.limit:
            raise StopIteration()

        if self._listing is None or self._list_index >= len(self._listing):
            self._next_batch()

        self._list_index += 1
        self.yielded += 1
        return self._listing[self._list_index - 1]

    def _next_batch(self):
        if self._exhausted:
            raise StopIteration()

        self._listing = self._reddit.get(self.url, params=self.params)
        if isinstance(self._listing, list):
            self._listing = self._listing[1]  # for submission duplicates
        elif isinstance(self._listing, dict):
            self._listing = FlairListing(self._reddit, self._listing)
        self._list_index = 0

        if not self._listing:
            raise StopIteration()

        if self._listing.after and self._listing.after != self.params.get(
            "after"
        ):
            self.params["after"] = self._listing.after
        else:
            self._exhausted = True

    def next(self):
        """Permit ListingGenerator to operate as a generator in py2."""
        return self.__next__()
