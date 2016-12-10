"""Provide the SubredditListingMixin class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from ..generator import ListingGenerator
from .base import BaseListingMixin
from .gilded import GildedListingMixin
from .rising import RisingListingMixin


class SubredditListingMixin(BaseListingMixin, GildedListingMixin,
                            RisingListingMixin):
    """Adds additional methods pertianing to Subreddit-like instances."""

    @property
    def comments(self):
        """An instance of :class:`.CommentHelper`.

        For example, to output the author of the 25 most recent comments of
        ``/r/redditdev`` execute:

        .. code:: python

           for comment in reddit.subreddit('redditdev').comments(limit=25):
               print(comment.author)

        """
        if self._comments is None:
            self._comments = CommentHelper(self)
        return self._comments

    def __init__(self, reddit, _data):
        """Initialize a SubredditListingMixin instance.

        :param reddit: An instance of :class:`.Reddit`.

        """
        super(SubredditListingMixin, self).__init__(reddit, _data)
        self._comments = None


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
        """Return a ListingGenerator for the Subreddit's comments.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method should be used in a way similar to the example below:

        .. code:: python

           for comment in reddit.subreddit('redditdev').comments(limit=25):
               print(comment.author)

        """
        return ListingGenerator(self._reddit, self._path, **generator_kwargs)
