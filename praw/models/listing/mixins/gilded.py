"""Provide the GildedListingMixin class."""
from ....compat import urljoin
from ...base import PRAWBase
from ..generator import ListingGenerator


class GildedListingMixin(PRAWBase):
    """Mixes in the gilded method."""

    def gilded(self, **generator_kwargs):
        """Return a ListingGenerator for gilded items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit, urljoin(self._path, "gilded"), **generator_kwargs
        )
