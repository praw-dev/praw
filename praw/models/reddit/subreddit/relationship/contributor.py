"""Provide the ContributorRelationship class."""

from .....const import API_PATH
from .relationship import SubredditRelationship


class ContributorRelationship(SubredditRelationship):
    """Provides methods to interact with a Subreddit's contributors.

    Contributors are also known as approved submitters.

    Contributors of a subreddit can be iterated through like so:

    .. code-block:: python

       for contributor in reddit.subreddit('redditdev').contributor():
           print(contributor)

    """

    def leave(self):
        """Abdicate the contributor position."""
        self.subreddit._reddit.post(
            API_PATH["leavecontributor"], data={"id": self.subreddit.fullname}
        )
