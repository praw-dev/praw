"""Provide the GildedListingMixin class."""
from typing import Any, Dict, Iterator, Union
from urllib.parse import urljoin

from ...base import PRAWBase
from ..generator import ListingGenerator


class GildedListingMixin(PRAWBase):
    """Mixes in the gilded method."""

    def gilded(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator[Any]:
        """Return a :class:`.ListingGenerator` for gilded items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to get gilded items in r/test:

        .. code-block:: python

            for item in reddit.subreddit("test").gilded():
                print(item.id)

        """
        return ListingGenerator(
            self._reddit, urljoin(self._path, "gilded"), **generator_kwargs
        )
