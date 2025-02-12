"""Provide the RisingListingMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urljoin

from praw.models.base import PRAWBase
from praw.models.listing.generator import ListingGenerator

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator

    import praw.models


class RisingListingMixin(PRAWBase):
    """Mixes in the rising methods."""

    def rising(self, **generator_kwargs: str | int | dict[str, str]) -> Iterator[praw.models.Submission]:
        """Return a :class:`.ListingGenerator` for rising submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to get rising submissions for r/test:

        .. code-block:: python

            for submission in reddit.subreddit("test").rising():
                print(submission.title)

        """
        return ListingGenerator(self._reddit, urljoin(self._path, "rising"), **generator_kwargs)
