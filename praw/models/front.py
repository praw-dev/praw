"""Provide the Front class."""
from typing import TYPE_CHECKING, Iterator, Union
from urllib.parse import urljoin

from .listing.generator import ListingGenerator
from .listing.mixins import SubredditListingMixin

if TYPE_CHECKING:  # pragma: no cover
    import praw


class Front(SubredditListingMixin):
    """Front is a Listing class that represents the front page."""

    def __init__(self, reddit: "praw.Reddit"):
        """Initialize a :class:`.Front` instance."""
        super().__init__(reddit, _data=None)
        self._path = "/"

    def best(
        self, **generator_kwargs: Union[str, int]
    ) -> Iterator["praw.models.Submission"]:
        """Return a :class:`.ListingGenerator` for best items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit, urljoin(self._path, "best"), **generator_kwargs
        )
