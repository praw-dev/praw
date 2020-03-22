"""Provide the SubredditRelationship class."""

from .....const import API_PATH
from ....listing.generator import ListingGenerator


class SubredditRelationship:
    """Represents a relationship between a redditor and subreddit.

    Instances of this class can be iterated through in order to discover the
    Redditors that make up the relationship.

    For example, banned users of a subreddit can be iterated through like so:

    .. code-block:: python

       for ban in reddit.subreddit('redditdev').banned():
           print('{}: {}'.format(ban, ban.note))

    """

    def __call__(self, redditor=None, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for Redditors in the relationship.

        :param redditor: When provided, yield at most a single
            :class:`~.Redditor` instance. This is useful to confirm if a
            relationship exists, or to fetch the metadata associated with a
            particular relationship (default: None).

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        self.subreddit.__class__._safely_add_arguments(
            generator_kwargs, "params", user=redditor
        )
        url = API_PATH["list_{}".format(self.relationship)].format(
            subreddit=self.subreddit
        )
        return ListingGenerator(
            self.subreddit._reddit, url, **generator_kwargs
        )

    def __init__(self, subreddit, relationship):
        """Create a SubredditRelationship instance.

        :param subreddit: The subreddit for the relationship.
        :param relationship: The name of the relationship.

        """
        self.relationship = relationship
        self.subreddit = subreddit

    def add(self, redditor, **other_settings):
        """Add ``redditor`` to this relationship.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        """
        data = {"name": str(redditor), "type": self.relationship}
        data.update(other_settings)
        url = API_PATH["friend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def remove(self, redditor):
        """Remove ``redditor`` from this relationship.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        """
        data = {"name": str(redditor), "type": self.relationship}
        url = API_PATH["unfriend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)
