"""Provide classes pertaining to listings."""

from six import text_type

from .redditmodel import RedditModel
from .redditor import Redditor
from .wikipage import WikiPage


class PRAWListing(RedditModel):
    """An abstract class to coerce a listing into RedditContentObjects."""

    CHILD_ATTRIBUTE = None

    def __init__(self, reddit):
        """Initialize a PRAWListing instance.

        :param reddit: An instance of :class:`~.Reddit`.

        """
        super(PRAWListing, self).__init__(reddit)

        if self.CHILD_ATTRIBUTE is None:
            raise NotImplementedError('PRAWListing must be extended.')

        child_list = getattr(self, self.CHILD_ATTRIBUTE)
        for index, item in enumerate(child_list):
            child_list[index] = self._convert(reddit, item)

    def __contains__(self, item):
        """Test if item exists in the listing."""
        return item in getattr(self, self.CHILD_ATTRIBUTE)

    def __delitem__(self, index):
        """Remove the item at position index from the listing."""
        del getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __getitem__(self, index):
        """Return the item at position index in the listing."""
        return getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __iter__(self):
        """Return an iterator to the listing."""
        return getattr(self, self.CHILD_ATTRIBUTE).__iter__()

    def __len__(self):
        """Return the number of items in the listing."""
        return len(getattr(self, self.CHILD_ATTRIBUTE))

    def __setitem__(self, index, item):
        """Set item at position `index` in the listing."""
        getattr(self, self.CHILD_ATTRIBUTE)[index] = item

    def __unicode__(self):
        """Return a string representation of the listing."""
        return text_type(getattr(self, self.CHILD_ATTRIBUTE))


class UserList(PRAWListing):
    """A list of Redditors. Works just like a regular list."""

    CHILD_ATTRIBUTE = 'children'

    @staticmethod
    def _convert(reddit, data):
        """Return a Redditor object from the data."""
        return Redditor(reddit, data['name'])


class WikiPageListing(PRAWListing):
    """A list of WikiPages. Works just like a regular list."""

    CHILD_ATTRIBUTE = '_tmp'

    @staticmethod
    def _convert(reddit, data):
        """Return a WikiPage object from the data."""
        subreddit = reddit._request_url.rsplit('/', 4)[1]
        return WikiPage(reddit, subreddit, data, fetch=False)
