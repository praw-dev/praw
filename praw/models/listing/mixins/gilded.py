"""Provide the GildedListingMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

from ...base import PRAWBase
from ..generator import ListingGenerator

if TYPE_CHECKING:
    from collections.abc import Iterator


class GildedListingMixin(PRAWBase):
    """Mixes in the gilded method."""

    def gilded(self, **generator_kwargs: str | int | dict[str, str]) -> Iterator[Any]:
        """Return a :class:`.ListingGenerator` for gilded items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to get gilded items in r/test:

        .. code-block:: python

            for item in reddit.subreddit("test").gilded():
                print(item.id)

        """
        return ListingGenerator(self._reddit, urljoin(self._path, "gilded"), **generator_kwargs)
