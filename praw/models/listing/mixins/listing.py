"""Provide the ListingMixin class."""
from .base import BaseListingMixin

class ListingMixin(BaseListingMixin):
    """Adds additional methods that apply to most Listing objects."""

    def gilded(self, **generator_kwargs):
        """Return a ListingGenerator for gilded items.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'gilded'),
                                **generator_kwargs)
