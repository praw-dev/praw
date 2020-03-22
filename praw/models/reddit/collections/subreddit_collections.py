"""Provide subreddit Collections functionality."""
from typing import Any, Dict, Optional, TypeVar

from ....const import API_PATH
from ....util.cache import cachedproperty
from ...base import PRAWBase
from ..subreddit import Subreddit
from .collection import Collection
from .subreddit_collections_moderation import SubredditCollectionsModeration

Reddit = TypeVar("Reddit")


class SubredditCollections(PRAWBase):
    r"""Class to represent a Subreddit's :class:`.Collection`\ s.

    Obtain an instance via:

    .. code-block:: python

       reddit.subreddit('SUBREDDIT').collections

    """

    @cachedproperty
    def mod(self) -> SubredditCollectionsModeration:
        """Get an instance of :class:`.SubredditCollectionsModeration`.

        Provides :meth:`~SubredditCollectionsModeration.create`:

        .. code-block:: python

           my_sub = reddit.subreddit('SUBREDDIT')
           new_collection = my_sub.collections.mod.create('Title', 'desc')

        """
        return SubredditCollectionsModeration(
            self._reddit, self.subreddit.fullname
        )

    def __call__(
        self,
        collection_id: Optional[str] = None,
        permalink: Optional[str] = None,
    ):
        """Return the :class:`.Collection` with the specified ID.

        :param collection_id: The ID of a Collection (default: None).
        :param permalink: The permalink of a Collection (default: None).
        :returns: The specified Collection.

        Exactly one of ``collection_id`` and ``permalink`` is required.

        Example usage:

        .. code-block:: python

           subreddit = reddit.subreddit('SUBREDDIT')

           uuid = '847e4548-a3b5-4ad7-afb4-edbfc2ed0a6b'
           collection = subreddit.collections(uuid)
           print(collection.title)
           print(collection.description)

           permalink = 'https://www.reddit.com/r/SUBREDDIT/collection/' + uuid
           collection = subreddit.collections(permalink=permalink)
           print(collection.title)
           print(collection.description)

        """
        if (collection_id is None) == (permalink is None):
            raise TypeError(
                "Exactly one of collection_id or permalink must "
                "be provided."
            )
        return Collection(
            self._reddit, collection_id=collection_id, permalink=permalink
        )

    def __init__(
        self,
        reddit: Reddit,
        subreddit: Subreddit,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize an instance of SubredditCollections."""
        super().__init__(reddit, _data)
        self.subreddit = subreddit

    def __iter__(self):
        r"""Iterate over the Subreddit's :class:`.Collection`\ s.

        Example usage:

        .. code-block:: python

           for collection in reddit.subreddit('SUBREDDIT').collections:
               print(collection.permalink)

        """
        request = self._reddit.get(
            API_PATH["collection_subreddit"],
            params={"sr_fullname": self.subreddit.fullname},
        )
        for collection in request:
            yield collection


Subreddit._subreddit_collections_class = SubredditCollections
