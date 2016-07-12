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

    def stream(self):
        """Yield new subreddits as they are created.

        Subreddits are yielded oldest first. Up to 100 historial subreddits
        will initially be returned.

        """
        return stream_generator(self.new)
