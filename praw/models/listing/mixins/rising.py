"""Provide the RisingListingMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urljoin

from praw.models.base import PRAWBase
from praw.models.listing.generator import ListingGenerator

if TYPE_CHECKING:
    from collections.abc import Iterator

    from typing_extensions import Unpack

    from praw import models
    from praw.models.listing.generator import ListingGeneratorKwargs


class RisingListingMixin(PRAWBase):
    """Mixes in the rising methods."""

    if TYPE_CHECKING:
        _path: str

    def rising(self, **generator_kwargs: Unpack[ListingGeneratorKwargs]) -> Iterator[models.Submission]:
        """Return a :class:`.ListingGenerator` for rising submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to get rising submissions for r/test:

        .. code-block:: python

            for submission in reddit.subreddit("test").rising():
                print(submission.title)

        """
        return ListingGenerator(self._reddit, urljoin(self._path, "rising"), **generator_kwargs)
