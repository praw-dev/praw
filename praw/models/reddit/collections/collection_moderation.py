"""Provide Collections moderation functionality."""
from typing import List, TypeVar, Union

from ....const import API_PATH
from ....exceptions import ClientException
from ...base import PRAWBase
from ..submission import Submission

Reddit = TypeVar("Reddit")


class CollectionModeration(PRAWBase):
    """Class to support moderation actions on a :class:`.Collection`.

    Obtain an instance via:

    .. code-block:: python

       reddit.subreddit('SUBREDDIT').collections('some_uuid').mod
    """

    def _post_fullname(self, post):
        """Get a post's fullname.

        :param post: A fullname, a Submission, a permalink, or an ID.
        :returns: The fullname of the post.
        """
        if isinstance(post, Submission):
            return post.fullname
        elif not isinstance(post, str):
            raise TypeError(
                "Cannot get fullname from object of type {}.".format(
                    type(post)
                )
            )
        if post.startswith(
            "{}_".format(self._reddit.config.kinds["submission"])
        ):
            return post
        try:
            return self._reddit.submission(url=post).fullname
        except ClientException:
            return self._reddit.submission(id=post).fullname

    def __init__(self, reddit: Reddit, collection_id: str):
        """Initialize an instance of CollectionModeration.

        :param collection_id: The ID of a collection.
        """
        super().__init__(reddit, _data=None)
        self.collection_id = collection_id

    def add_post(self, submission: Submission):
        """Add a post to the collection.

        :param submission: The post to add, a :class:`.Submission`, its
            permalink as a ``str``, its fullname as a ``str``, or its ID as a
            ``str``.

        Example usage:

        .. code-block:: python

           collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
           collection.mod.add_post('bgibu9')

        See also :meth:`.remove_post`.

        """
        link_fullname = self._post_fullname(submission)

        self._reddit.post(
            API_PATH["collection_add_post"],
            data={
                "collection_id": self.collection_id,
                "link_fullname": link_fullname,
            },
        )

    def delete(self):
        """Delete this collection.

        Example usage:

        .. code-block:: python

           reddit.subreddit('SUBREDDIT').collections('some_uuid').mod.delete()

        See also :meth:`~.SubredditCollectionsModeration.create`.

        """
        self._reddit.post(
            API_PATH["collection_delete"],
            data={"collection_id": self.collection_id},
        )

    def remove_post(self, submission: Submission):
        """Remove a post from the collection.

        :param submission: The post to remove, a :class:`.Submission`, its
            permalink as a ``str``, its fullname as a ``str``, or its ID as a
            ``str``.

        Example usage:

        .. code-block:: python

           collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
           collection.mod.remove_post('bgibu9')

        See also :meth:`.add_post`.

        """
        link_fullname = self._post_fullname(submission)

        self._reddit.post(
            API_PATH["collection_remove_post"],
            data={
                "collection_id": self.collection_id,
                "link_fullname": link_fullname,
            },
        )

    def reorder(self, links: List[Union[str, Submission]]):
        """Reorder posts in the collection.

        :param links: A ``list`` of submissions, as :class:`.Submission`,
            permalink as a ``str``, fullname as a ``str``, or ID as a ``str``.

        Example usage:

        .. code-block:: python

           collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
           current_order = collection.link_ids
           new_order = reversed(current_order)
           collection.mod.reorder(new_order)

        """
        link_ids = ",".join(self._post_fullname(post) for post in links)
        self._reddit.post(
            API_PATH["collection_reorder"],
            data={"collection_id": self.collection_id, "link_ids": link_ids},
        )

    def update_description(self, description: str):
        """Update the collection's description.

        :param description: The new description.

        Example usage:

        .. code-block:: python

           collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
           collection.mod.update_description('Please enjoy these links!')

        See also :meth:`.update_title`.

        """
        self._reddit.post(
            API_PATH["collection_desc"],
            data={
                "collection_id": self.collection_id,
                "description": description,
            },
        )

    def update_title(self, title: str):
        """Update the collection's title.

        :param title: The new title.

        Example usage:

        .. code-block:: python

           collection = reddit.subreddit('SUBREDDIT').collections('some_uuid')
           collection.mod.update_title('Titley McTitleface')

        See also :meth:`.update_description`.

        """
        self._reddit.post(
            API_PATH["collection_title"],
            data={"collection_id": self.collection_id, "title": title},
        )
