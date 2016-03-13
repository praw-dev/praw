"""Provide classes that act as lists."""

from six import text_type

from .prawmodel import PRAWModel
from .redditor import Redditor
from .wikipage import WikiPage


class PRAWList(PRAWModel):
    """An abstract class to coerce a list into a PRAWModel."""

    CHILD_ATTRIBUTE = None

    @staticmethod
    def _convert(reddit, item):
        raise NotImplementedError('PRAWList must be extended.')

    def __init__(self, reddit):
        """Initialize a PRAWList instance.

        :param reddit: An instance of :class:`~.Reddit`.

        """
        super(PRAWList, self).__init__(reddit)

        if self.CHILD_ATTRIBUTE is None:
            raise NotImplementedError('PRAWList must be extended.')

        child_list = getattr(self, self.CHILD_ATTRIBUTE)
        for index, item in enumerate(child_list):
            child_list[index] = self._convert(reddit, item)

    def __contains__(self, item):
        """Test if item exists in the list."""
        return item in getattr(self, self.CHILD_ATTRIBUTE)

    def __delitem__(self, index):
        """Remove the item at position index from the list."""
        del getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __getitem__(self, index):
        """Return the item at position index in the list."""
        return getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __iter__(self):
        """Return an iterator to the list."""
        return getattr(self, self.CHILD_ATTRIBUTE).__iter__()

    def __len__(self):
        """Return the number of items in the list."""
        return len(getattr(self, self.CHILD_ATTRIBUTE))

    def __setitem__(self, index, item):
        """Set item at position `index` in the list."""
        getattr(self, self.CHILD_ATTRIBUTE)[index] = item

    def __unicode__(self):
        """Return a string representation of the list."""
        return text_type(getattr(self, self.CHILD_ATTRIBUTE))


class UserList(PRAWList):
    """A list of Redditors. Works just like a regular list."""

    CHILD_ATTRIBUTE = 'children'

    @staticmethod
    def _convert(reddit, data):
        """Return a Redditor object from the data."""
        return Redditor(reddit, data['name'])


class WikiPageList(PRAWList):
    """A list of WikiPages. Works just like a regular list."""

    CHILD_ATTRIBUTE = '_tmp'

    @staticmethod
    def _convert(reddit, data):
        """Return a WikiPage object from the data."""
        subreddit = reddit._request_url.rsplit('/', 4)[1]
        return WikiPage(reddit, subreddit, data, fetch=False)
