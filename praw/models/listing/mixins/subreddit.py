"""Provide the SubredditListingMixin class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from ..generator import ListingGenerator
from .base import BaseListingMixin
from .gilded import GildedListingMixin


class SubredditListingMixin(BaseListingMixin, GildedListingMixin):
    """Adds additional methods pertianing to Subreddit-like instances."""

    def comments(self, **generator_kwargs):
        """Return a ListingGenerator for the Subreddit's comments."""
        return ListingGenerator(self._reddit, urljoin(self._path, 'comments'),
                                **generator_kwargs)

    def rising(self, **generator_kwargs):
        """Return a ListingGenerator for rising submissions.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'rising'),
                                **generator_kwargs)
