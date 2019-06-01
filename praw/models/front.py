"""Provide the Front class."""
from ..compat import urljoin
from .listing.generator import ListingGenerator
from .listing.mixins import SubredditListingMixin


class Front(SubredditListingMixin):
    """Front is a Listing class that represents the front page."""

    def __init__(self, reddit):
        """Initialize a Front instance."""
        super(Front, self).__init__(reddit, _data=None)
        self._path = "/"

    def best(self, **generator_kwargs):
        """Return a ListingGenerator for best items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit, urljoin(self._path, "best"), **generator_kwargs
        )
