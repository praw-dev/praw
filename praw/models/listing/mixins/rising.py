"""Provide the RisingListingMixin class."""
from ....compat import urljoin
from ...base import PRAWBase
from ..generator import ListingGenerator


class RisingListingMixin(PRAWBase):
    """Mixes in the rising methods."""

    def random_rising(self, **generator_kwargs):
        """Return a ListingGenerator for random rising submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit,
            urljoin(self._path, "randomrising"),
            **generator_kwargs
        )

    def rising(self, **generator_kwargs):
        """Return a ListingGenerator for rising submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit, urljoin(self._path, "rising"), **generator_kwargs
        )
