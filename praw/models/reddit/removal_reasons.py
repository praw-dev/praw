"""Provide the Reason class."""
from typing import Any, Dict, Generator, Optional, TypeVar, Union

from ...const import API_PATH
from ...exceptions import ClientException
from .base import RedditBase

_RemovalReason = TypeVar("_RemovalReason")
Reddit = TypeVar("Reddit")
Subreddit = TypeVar("Subreddit")


class RemovalReason(RedditBase):
    """An individual Removal Reason object.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``id``                  The id of the removal reason.
    ``message``             The message of the removal reason.
    ``title``               The title of the removal reason.
    ======================= ===================================================
    """

    STR_FIELD = "id"

    def __eq__(self, other: Union[str, _RemovalReason]) -> bool:
        """Return whether the other instance equals the current."""
        if isinstance(other, str):
            return other == str(self)
        return isinstance(other, self.__class__) and str(self) == str(other)

    def __hash__(self) -> int:
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self))

    def __init__(
        self,
        reddit: Reddit,
        subreddit: Subreddit,
        reason_id: str,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Construct an instance of the Removal Reason object."""
        self.id = reason_id
        self.subreddit = subreddit
        super().__init__(reddit, _data=_data)

    def _fetch(self):
        for removal_reason in self.subreddit.mod.removal_reasons:
            if removal_reason.id == self.id:
                self.__dict__.update(removal_reason.__dict__)
                self._fetched = True
                return
        raise ClientException(
            "r/{} does not have the removal reason {}".format(
                self.subreddit, self.id
            )
        )

    def delete(self):
        """Delete a removal reason from this subreddit.

        To delete ``'141vv5c16py7d'`` from the subreddit ``'NAME'`` try:

        .. code-block:: python

           reddit.subreddit('NAME').removal_reasons['141vv5c16py7d'].mod.delete()

        """
        url = API_PATH["removal_reason"].format(
            subreddit=self.subreddit, id=self.id
        )
        self.subreddit._reddit.request("DELETE", url)

    def update(self, message: str, title: str):
        """Update the removal reason from this subreddit.

        :param message: The removal reason's new message (required).
        :param title: The removal reason's new title (required).

        To update ``'141vv5c16py7d'`` from the subreddit ``'NAME'`` try:

        .. code-block:: python

           reddit.subreddit('NAME').removal_reasons['141vv5c16py7d'].mod.update(
               message='New message',
               title='New title')

        """
        url = API_PATH["removal_reason"].format(
            subreddit=self.subreddit, id=self.id
        )
        data = {"message": message, "title": title}
        self.subreddit._reddit.put(url, data=data)


class SubredditRemovalReasons:
    """Provide a set of functions to a Subreddit's removal reasons."""

    def __getitem__(self, reason_id: str) -> RemovalReason:
        """Lazily return the Removal Reason for the subreddit with id ``reason_id``.

        :param reason_id: The id of the removal reason

        This method is to be used to fetch a specific removal reason, like so:

        .. code-block:: python

           reason_id = '141vv5c16py7d'
           reason = reddit.subreddit('NAME').mod.removal_reasons[reason_id]
           print(reason)

        """
        return RemovalReason(self.subreddit._reddit, self.subreddit, reason_id)

    def __init__(self, subreddit: Subreddit):
        """Create a SubredditRemovalReasons instance.

        :param subreddit: The subreddit whose removal reasons to work with.

        """
        self.subreddit = subreddit
        self._reddit = subreddit._reddit

    def __iter__(self) -> Generator[RemovalReason, None, None]:
        """Return a list of Removal Reasons for the subreddit.

        This method is used to discover all removal reasons for a
        subreddit:

        .. code-block:: python

           for removal_reason in reddit.subreddit('NAME').mod.removal_reasons:
               print(removal_reason)

        """
        response = self.subreddit._reddit.get(
            API_PATH["removal_reasons_list"].format(subreddit=self.subreddit)
        )
        for reason_id, reason_data in response["data"].items():
            yield RemovalReason(
                self._reddit, self.subreddit, reason_id, _data=reason_data
            )

    def add(self, message: str, title: str) -> RemovalReason:
        """Add a removal reason to this subreddit.

        :param message: The message associated with the removal reason.
        :param title: The title of the removal reason
        :returns: The RemovalReason added.

        The message will be prepended with `Hi u/username,` automatically.

        To add ``'Test'`` to the subreddit ``'NAME'`` try:

        .. code-block:: python

           reddit.subreddit('NAME').removal_reasons.mod.add(
               message='Foobar',
               title='Test')

        """
        data = {"message": message, "title": title}
        url = API_PATH["removal_reasons_list"].format(subreddit=self.subreddit)
        reason_id = self.subreddit._reddit.post(url, data=data)
        return RemovalReason(self._reddit, self.subreddit, reason_id)
