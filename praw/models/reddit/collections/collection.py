"""Provide Collections functionality."""
from typing import Any, Dict, Generator, Optional, TypeVar

from ....const import API_PATH
from ....exceptions import ClientException
from ....util.cache import cachedproperty
from ..base import RedditBase
from ..subreddit import Subreddit
from .collection_moderation import CollectionModeration

Reddit = TypeVar("Reddit")


class Collection(RedditBase):
    """Class to represent a Collection.

    Obtain an instance via:

    .. code-block:: python

       collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')

    or

    .. code-block:: python

       collection = reddit.subreddit('SUBREDDIT').collections(
           permalink='https://reddit.com/r/SUBREDDIT/collection/some_uuid')

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor that they
    will be the only attributes present.

    ======================= ==================================================
    Attribute               Description
    ======================= ==================================================
    ``author``              The :class:`.Redditor` who created the collection.
    ``collection_id``       The UUID of the collection.
    ``created_at_utc``      Time the collection was created, represented in
                            `Unix Time`_.
    ``description``         The collection description.
    ``last_update_utc``     Time the collection was last updated, represented
                            in `Unix Time`_.
    ``link_ids``            A ``list`` of :class:`.Submission` fullnames.
    ``permalink``           The collection's permalink (to view on the web).
    ``sorted_links``        An iterable listing of the posts in
                            this collection.
    ``title``               The title of the collection.
    ======================= ==================================================

    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time

    """

    STR_FIELD = "collection_id"

    @cachedproperty
    def mod(self) -> CollectionModeration:
        """Get an instance of :class:`.CollectionModeration`.

        Provides access to various methods, including
        :meth:`~reddit.collections.CollectionModeration.add_post`,
        :meth:`~reddit.collections.CollectionModeration.delete`,
        :meth:`~reddit.collections.CollectionModeration.reorder`,
        and :meth:`~reddit.collections.CollectionModeration.update_title`.

        Example usage:

        .. code-block:: python

           collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
           collection.mod.update_title('My new title!')

        """
        return CollectionModeration(self._reddit, self.collection_id)

    @cachedproperty
    def subreddit(self) -> Subreddit:
        """Get the subreddit that this collection belongs to.

        For example:

        .. code-block:: python

            collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
            subreddit = collection.subreddit

        """
        return next(self._reddit.info([self.subreddit_id]))

    def __init__(
        self,
        reddit: Reddit,
        _data: Dict[str, Any] = None,
        collection_id: Optional[str] = None,
        permalink: Optional[str] = None,
    ):
        """Initialize this collection.

        :param reddit: An instance of :class:`.Reddit`.
        :param _data: Any data associated with the Collection (optional).
        :param collection_id: The ID of the Collection (optional).
        :param permalink: The permalink of the Collection (optional).
        """
        super().__init__(reddit, _data)

        if (_data, collection_id, permalink).count(None) != 2:
            raise TypeError(
                "Exactly one of _data, collection_id, "
                "or permalink must be provided."
            )

        if permalink is not None:
            collection_id = self._url_parts(permalink)[4]

        if collection_id is not None:
            self.collection_id = collection_id  # set from _data otherwise

        self._info_params = {
            "collection_id": self.collection_id,
            "include_links": True,
        }

    def __iter__(self) -> Generator[Any, None, None]:
        """Provide a way to iterate over the posts in this Collection.

        Example usage:

        .. code-block:: python

           collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
           for submission in collection:
               print(submission.title, submission.permalink)

        """
        for item in self.sorted_links:
            yield item

    def __len__(self) -> int:
        """Get the number of posts in this Collection.

        Example usage:

        .. code-block:: python

           collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
           print(len(collection))

        """
        return len(self.link_ids)

    def __setattr__(self, attribute: str, value: Any):
        """Objectify author, subreddit, and sorted_links attributes."""
        if attribute == "author_name":
            self.author = self._reddit.redditor(value)
        elif attribute == "sorted_links":
            value = self._reddit._objector.objectify(value)
        super().__setattr__(attribute, value)

    def _fetch_info(self):
        return ("collection", {}, self._info_params)

    def _fetch_data(self):
        name, fields, params = self._fetch_info()
        path = API_PATH[name].format(**fields)
        return self._reddit.request("GET", path, params)

    def _fetch(self):
        data = self._fetch_data()
        try:
            self._reddit._objector.check_error(data)
        except ClientException:
            # A well-formed but invalid Collections ID during fetch time
            # causes Reddit to return something that looks like an error
            # but with no content.
            raise ClientException(
                "Error during fetch. Check collection "
                "ID {!r} is correct.".format(self.collection_id)
            )

        other = type(self)(self._reddit, _data=data)
        self.__dict__.update(other.__dict__)
        self._fetched = True

    def follow(self):
        """Follow this Collection.

        Example usage:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').collections('some_uuid').follow()

        See also :meth:`~.unfollow`.
        """
        self._reddit.post(
            API_PATH["collection_follow"],
            data={"collection_id": self.collection_id, "follow": True},
        )

    def unfollow(self):
        """Unfollow this Collection.

        Example usage:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').collections('some_uuid').unfollow()

        See also :meth:`~.follow`.
        """
        self._reddit.post(
            API_PATH["collection_follow"],
            data={"collection_id": self.collection_id, "follow": False},
        )
