"""Provide the SubredditListingMixin class."""
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Union
from urllib.parse import urljoin

from ....util.cache import cachedproperty
from ...base import PRAWBase
from ..generator import ListingGenerator
from .base import BaseListingMixin
from .gilded import GildedListingMixin
from .rising import RisingListingMixin

if TYPE_CHECKING:  # pragma: no cover
    import praw


class CommentHelper(PRAWBase):
    """Provide a set of functions to interact with a :class:`.Subreddit`'s comments."""

    @property
    def _path(self) -> str:
        return urljoin(self.subreddit._path, "comments/")

    def __call__(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator["praw.models.Comment"]:
        """Return a :class:`.ListingGenerator` for the :class:`.Subreddit`'s comments.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method should be used in a way similar to the example below:

        .. code-block:: python

            for comment in reddit.subreddit("test").comments(limit=25):
                print(comment.author)

        """
        return ListingGenerator(self._reddit, self._path, **generator_kwargs)

    def __init__(self, subreddit: "praw.models.Subreddit"):
        """Initialize a :class:`.CommentHelper` instance."""
        super().__init__(subreddit._reddit, _data=None)
        self.subreddit = subreddit


class SubredditListingMixin(BaseListingMixin, GildedListingMixin, RisingListingMixin):
    """Adds additional methods pertaining to subreddit-like instances."""

    @cachedproperty
    def comments(self) -> CommentHelper:
        """Provide an instance of :class:`.CommentHelper`.

        For example, to output the author of the 25 most recent comments of r/test
        execute:

        .. code-block:: python

            for comment in reddit.subreddit("test").comments(limit=25):
                print(comment.author)

        """
        return CommentHelper(self)

    def __init__(self, reddit: "praw.Reddit", _data: Optional[Dict[str, Any]]):
        """Initialize a :class:`.SubredditListingMixin` instance.

        :param reddit: An instance of :class:`.Reddit`.

        """
        super().__init__(reddit, _data=_data)
