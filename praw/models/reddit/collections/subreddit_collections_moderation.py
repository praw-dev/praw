"""Provide subreddit Collections moderation functionality."""
from typing import Any, Dict, Optional, TypeVar

from ....const import API_PATH
from ...base import PRAWBase

Reddit = TypeVar("Reddit")


class SubredditCollectionsModeration(PRAWBase):
    """Class to represent moderator actions on a Subreddit's Collections.

    Obtain an instance via:

    .. code-block:: python

       reddit.subreddit('SUBREDDIT').collections.mod

    """

    def __init__(
        self,
        reddit: Reddit,
        sub_fullname: str,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the SubredditCollectionsModeration instance."""
        super().__init__(reddit, _data)
        self.subreddit_fullname = sub_fullname

    def create(self, title: str, description: str):
        """Create a new :class:`.Collection`.

        The authenticated account must have appropriate moderator
        permissions in the subreddit this collection belongs to.

        :param title: The title of the collection, up to 300 characters.
        :param description: The description, up to 500 characters.

        :returns: The newly created :class:`.Collection`.

        Example usage:

        .. code-block:: python

           my_sub = reddit.subreddit('SUBREDDIT')
           new_collection = my_sub.collections.mod.create('Title', 'desc')
           new_collection.mod.add_post('bgibu9')

        See also :meth:`~CollectionModeration.delete`.

        """
        return self._reddit.post(
            API_PATH["collection_create"],
            data={
                "sr_fullname": self.subreddit_fullname,
                "title": title,
                "description": description,
            },
        )
