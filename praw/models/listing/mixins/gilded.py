"""Provide the ListingMixin class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from .base import BaseListingMixin
from ..generator import ListingGenerator


class ListingMixin(BaseListingMixin):
    """Adds additional methods that apply to most Listing objects."""

    def gilded(self, **generator_kwargs):
        """Return a ListingGenerator for gilded items.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'gilded'),
                                **generator_kwargs)
