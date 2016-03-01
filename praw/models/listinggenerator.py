"""Provide the ListingGenerator class."""

from .prawmodel import PRAWModel


class ListingGenerator(PRAWModel):
    """Instances of this class generate ``RedditModels``."""

    def __init__(self, reddit, url, limit=100, params=None):
        """Initialize a ListingGenerator instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param url: A URL returning a reddit listing.
        :param limit: The number of content entries to fetch. If ``limit`` is
            None, then fetch as many entries as possible. Most of reddit's
            listings contain a maximum of 1000 items, and are returned 100 at a
            time. This class will automatically issue all necessary
            requests. (Default: 100)
        :param params: A dictionary containing additional query string
            parameters to send with the request.

        """
        super(ListingGenerator, self).__init__(reddit)
        self._exhausted = False
        self._list = None
        self._list_index = None
        self._reddit = reddit
        self.after_field = 'after'
        self.extract_list_index = None
        self.limit = limit
        self.params = params or {}
        self.root_field = 'data'
        self.thing_list_field = 'children'
        self.url = url
        self.yielded = 0

        self.params['limit'] = self.limit or 1024

    def __iter__(self):
        """Permit ListingGenerator to operate as an iterator."""
        return self

    def __next__(self):
        """Permit ListingGenerator to operate as a generator."""
        if self.limit is not None and self.yielded >= self.limit:
            raise StopIteration()

        if self._list is None or self._list_index >= len(self._list):
            self._next_batch()

        self._list_index += 1
        self.yielded += 1
        return self._list[self._list_index - 1]

    def _next_batch(self):
        if self._exhausted:
            raise StopIteration()

        page_data = self._reddit.request(self.url, params=self.params)
        if self.extract_list_index is not None:
            page_data = page_data[self.extract_list_index]

        root = page_data[self.root_field]
        self._list = root[self.thing_list_field]
        self._list_index = 0

        if len(self._list) == 0:
            raise StopIteration()

        if root.get(self.after_field):
            self.params['after'] = root[self.after_field]
        else:
            self._exhausted = True

    def next(self):
        return self.__next__()
