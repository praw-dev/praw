"""Provide the Subreddits class."""
from .base import PRAWBase
from .listing.generator import ListingGenerator
from .util import stream_generator
from ..const import API_PATH


class Subreddits(PRAWBase):
    """Subreddits is a Listing class that provides various subreddit lists."""

    def default(self, **generator_kwargs):
        """Return a ListingGenerator for default subreddits."""
        return ListingGenerator(self._reddit, API_PATH['subreddits_default'],
                                **generator_kwargs)

    def gold(self, **generator_kwargs):
        """Return a ListingGenerator for gold subreddits."""
        return ListingGenerator(self._reddit, API_PATH['subreddits_gold'],
                                **generator_kwargs)

    def new(self, **generator_kwargs):
        """Return a ListingGenerator for new subreddits."""
        return ListingGenerator(self._reddit, API_PATH['subreddits_new'],
                                **generator_kwargs)

    def popular(self, **generator_kwargs):
        """Return a ListingGenerator for default subreddits."""
        return ListingGenerator(self._reddit, API_PATH['subreddits_popular'],
                                **generator_kwargs)

    def search(self, query, **generator_kwargs):
        """Return a ListingGenerator of subreddits matching ``query``.

        Subreddits are searched by both their title and description. To search
        names only see ``search_by_name``.

        :param query: The query string to filter subreddits by.

        """
        self._safely_add_arguments(generator_kwargs, 'params', q=query)
        return ListingGenerator(self._reddit, API_PATH['subreddits_search'],
                                **generator_kwargs)

    def search_by_name(self, query, include_nsfw=True, exact=False):
        """Return list of Subreddits whose names begin with ``query``.

        :param query: Search for subreddits beginning with this string.
        :param include_nsfw: Include subreddits labeled NSFW (default: True).
        :param exact: Return only exact matches to ``query`` (default: False).

        """
        result = self._reddit.post(API_PATH['subreddits_name_search'],
                                   data={'include_over_18': include_nsfw,
                                         'exact': exact, 'query': query})
        return [self._reddit.subreddit(x) for x in result['names']]

    def stream(self):
        """Yield new subreddits as they are created.

        Subreddits are yielded oldest first. Up to 100 historial subreddits
        will initially be returned.

        """
        return stream_generator(self.new)
