"""Provide the GildedListingMixin class."""
from typing import Any, Dict, Generator, Union
from urllib.parse import urljoin

from ...base import PRAWBase
from ..generator import ListingGenerator


class GildedListingMixin(PRAWBase):
    """Mixes in the gilded method."""

    def gilded(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Generator[Any, None, None]:
        """Return a :class:`.ListingGenerator` for gilded items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit, urljoin(self._path, "gilded"), **generator_kwargs
        )
