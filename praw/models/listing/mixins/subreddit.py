"""Provide the SubredditListingMixin class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from ..generator import ListingGenerator
from .base import BaseListingMixin
from .gilded import GildedListingMixin


class SubredditListingMixin(BaseListingMixin, GildedListingMixin):
    """Adds additional methods pertianing to Subreddit-like instances."""

    def __init__(self, reddit, _data):
        """Initialize a SubredditListingMixin instance.

        :param reddit: An instance of :class:`.Reddit`.

        """
        super(SubredditListingMixin, self).__init__(reddit, _data)
        self.comments = CommentHelper(self)

    def rising(self, **generator_kwargs):
        """Return a ListingGenerator for rising submissions.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'rising'),
                                **generator_kwargs)


class CommentHelper(GildedListingMixin):
    """Provide a set of functions to interact with a subreddit's comments."""

    @property
    def _path(self):
        return urljoin(self.subreddit._path, 'comments/')

    def __init__(self, subreddit):
        """Initialize a CommentHelper instance."""
        super(CommentHelper, self).__init__(subreddit._reddit, None)
        self.subreddit = subreddit

    def __call__(self, **generator_kwargs):
        """Return a ListingGenerator for the Subreddit's comments."""
        return ListingGenerator(self._reddit, self._path, **generator_kwargs)
