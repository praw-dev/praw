"""Provide the Redditors class."""
from .base import PRAWBase
from .listing.generator import ListingGenerator
from .util import stream_generator
from ..const import API_PATH


class Redditors(PRAWBase):
    """Redditors is a Listing class that provides various Redditor lists."""

    def new(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for new Redditors.

        :returns Redditor profiles, which are a type of :class:`.Subreddit`.
        """
        return ListingGenerator(
            self._reddit, API_PATH["users_new"], **generator_kwargs
        )

    def popular(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for popular Redditors.

        :returns Redditor profiles, which are a type of :class:`.Subreddit`.
        """
        return ListingGenerator(
            self._reddit, API_PATH["users_popular"], **generator_kwargs
        )

    def search(self, query, **generator_kwargs):
        r"""Return a :class:`.ListingGenerator` of Redditors for ``query``.

        :param query: The query string to filter Redditors by.

        :returns :class:`.Redditor`\ s.

        """
        self._safely_add_arguments(generator_kwargs, "params", q=query)
        return ListingGenerator(
            self._reddit, API_PATH["users_search"], **generator_kwargs
        )

    def stream(self, **stream_options):
        """Yield new Redditors as they are created.

        Redditors are yielded oldest first. Up to 100 historical Redditors
        will initially be returned.

        Keyword arguments are passed to :func:`.stream_generator`.

        :returns Redditor profiles, which are a type of :class:`.Subreddit`.
        """
        return stream_generator(self.new, **stream_options)
