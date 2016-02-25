"""Provide classes pertaining to listings."""

from six import text_type

from .redditcontentobject import RedditContentObject
from .redditor import Redditor
from .wikipage import WikiPage


class PRAWListing(RedditContentObject):
    """An abstract class to coerce a listing into RedditContentObjects."""

    CHILD_ATTRIBUTE = None

    def __init__(self, reddit_session, json_dict=None, fetch=False):
        """Construct an instance of the PRAWListing object."""
        super(PRAWListing, self).__init__(reddit_session, json_dict, fetch)

        if not self.CHILD_ATTRIBUTE:
            raise NotImplementedError('PRAWListing must be extended.')

        child_list = getattr(self, self.CHILD_ATTRIBUTE)
        for index, item in enumerate(child_list):
            child_list[index] = self._convert(reddit_session, item)

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
    def _convert(reddit_session, data):
        """Return a Redditor object from the data."""
        retval = Redditor(reddit_session, data['name'], fetch=False)
        retval.id = data['id'].split('_')[1]  # pylint: disable=C0103,W0201
        return retval


class WikiPageListing(PRAWListing):
    """A list of WikiPages. Works just like a regular list."""

    CHILD_ATTRIBUTE = '_tmp'

    @staticmethod
    def _convert(reddit_session, data):
        """Return a WikiPage object from the data."""
        # TODO: The _request_url hack shouldn't be necessary
        # pylint: disable=W0212
        subreddit = reddit_session._request_url.rsplit('/', 4)[1]
        # pylint: enable=W0212
        return WikiPage(reddit_session, subreddit, data, fetch=False)
