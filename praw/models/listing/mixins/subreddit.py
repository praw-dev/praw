"""Provide the SubredditListingMixin class."""
from .listing import ListingMixin


class SubredditListingMixin(ListingMixin):
    """Adds additional methods pertianing to Subreddit-like instances."""

    def rising(self, **generator_kwargs):
        """Return a ListingGenerator for rising submissions.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'rising'),
                                **generator_kwargs)
