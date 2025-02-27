"""Provide the Front class."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urljoin

from praw.models.listing.generator import ListingGenerator
from praw.models.listing.mixins import SubredditListingMixin

if TYPE_CHECKING:
    from collections.abc import Iterator

    import praw.models


class Front(SubredditListingMixin):
    """Front is a Listing class that represents the front page."""

    def __init__(self, reddit: praw.Reddit) -> None:
        """Initialize a :class:`.Front` instance."""
        super().__init__(reddit, _data=None)
        self._path = "/"

    def best(self, **generator_kwargs: str | int) -> Iterator[praw.models.Submission]:
        """Return a :class:`.ListingGenerator` for best items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, "best"), **generator_kwargs)
