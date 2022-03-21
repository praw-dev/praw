"""Provide the RisingListingMixin class."""
from typing import TYPE_CHECKING, Dict, Iterator, Union
from urllib.parse import urljoin

from ...base import PRAWBase
from ..generator import ListingGenerator

if TYPE_CHECKING:  # pragma: no cover
    import praw


class RisingListingMixin(PRAWBase):
    """Mixes in the rising methods."""

    def random_rising(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator["praw.models.Submission"]:
        """Return a :class:`.ListingGenerator` for random rising submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to get random rising submissions for r/test:

        .. code-block:: python

            for submission in reddit.subreddit("test").random_rising():
                print(submission.title)

        """
        return ListingGenerator(
            self._reddit, urljoin(self._path, "randomrising"), **generator_kwargs
        )

    def rising(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator["praw.models.Submission"]:
        """Return a :class:`.ListingGenerator` for rising submissions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        For example, to get rising submissions for r/test:

        .. code-block:: python

            for submission in reddit.subreddit("test").rising():
                print(submission.title)

        """
        return ListingGenerator(
            self._reddit, urljoin(self._path, "rising"), **generator_kwargs
        )
