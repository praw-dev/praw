"""Provide the Removal Reason class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from praw.const import API_PATH
from praw.exceptions import ClientException
from praw.util import cachedproperty

from .base import RedditBase

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator

    import praw


class RemovalReason(RedditBase):
    """An individual Removal Reason object.

    .. include:: ../../typical_attributes.rst

    =========== ==================================
    Attribute   Description
    =========== ==================================
    ``id``      The ID of the removal reason.
    ``message`` The message of the removal reason.
    ``title``   The title of the removal reason.
    =========== ==================================

    """

    STR_FIELD = "id"

    def __eq__(self, other: str | RemovalReason) -> bool:
        """Return whether the other instance equals the current."""
        if isinstance(other, str):
            return other == str(self)
        return isinstance(other, self.__class__) and str(self) == str(other)

    def __hash__(self) -> int:
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(str(self))

    def __init__(
        self,
        reddit: praw.Reddit,
        subreddit: praw.models.Subreddit,
        id: str | None = None,
        _data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a :class:`.RemovalReason` instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param subreddit: An instance of :class:`.Subreddit`.
        :param id: The ID of the removal reason.

        """
        if (id, _data).count(None) != 1:
            msg = "Either id or _data needs to be given."
            raise ValueError(msg)

        if id:
            self.id = id
        self.subreddit = subreddit
        super().__init__(reddit, _data=_data)

    def _fetch(self) -> None:
        for removal_reason in self.subreddit.mod.removal_reasons:
            if removal_reason.id == self.id:
                self.__dict__.update(removal_reason.__dict__)
                super()._fetch()
                return
        msg = f"Subreddit {self.subreddit} does not have the removal reason {self.id}"
        raise ClientException(msg)

    def delete(self) -> None:
        """Delete a removal reason from this subreddit.

        To delete ``"141vv5c16py7d"`` from r/test try:

        .. code-block:: python

            reddit.subreddit("test").mod.removal_reasons["141vv5c16py7d"].delete()

        """
        url = API_PATH["removal_reason"].format(subreddit=self.subreddit, id=self.id)
        self._reddit.delete(url)

    def update(self, *, message: str | None = None, title: str | None = None) -> None:
        """Update the removal reason from this subreddit.

        .. note::

            Existing values will be used for any unspecified arguments.

        :param message: The removal reason's new message.
        :param title: The removal reason's new title.

        To update ``"141vv5c16py7d"`` from r/test try:

        .. code-block:: python

            reddit.subreddit("test").mod.removal_reasons["141vv5c16py7d"].update(
                title="New title", message="New message"
            )

        """
        url = API_PATH["removal_reason"].format(subreddit=self.subreddit, id=self.id)
        data = {
            name: getattr(self, name) if value is None else value
            for name, value in {"message": message, "title": title}.items()
        }
        self._reddit.put(url, data=data)


class SubredditRemovalReasons:
    """Provide a set of functions to a :class:`.Subreddit`'s removal reasons."""

    @cachedproperty
    def _removal_reason_list(self) -> list[RemovalReason]:
        """Get a list of Removal Reason objects.

        :returns: A list of instances of :class:`.RemovalReason`.

        """
        response = self._reddit.get(API_PATH["removal_reasons_list"].format(subreddit=self.subreddit))
        return [
            RemovalReason(self._reddit, self.subreddit, _data=response["data"][reason_id])
            for reason_id in response["order"]
        ]

    def __getitem__(self, reason_id: str | int | slice) -> RemovalReason:
        """Return the Removal Reason with the ID/number/slice ``reason_id``.

        :param reason_id: The ID or index of the removal reason

        .. note::

            Removal reasons fetched using a specific rule name are lazily loaded, so you
            might have to access an attribute to get all the expected attributes.

        This method is to be used to fetch a specific removal reason, like so:

        .. code-block:: python

            reason_id = "141vv5c16py7d"
            reason = reddit.subreddit("test").mod.removal_reasons[reason_id]
            print(reason)

        You can also use indices to get a numbered removal reason. Since Python uses
        0-indexing, the first removal reason is index 0, and so on.

        .. note::

            Both negative indices and slices can be used to interact with the removal
            reasons.

        :raises: :py:class:`IndexError` if a removal reason of a specific number does
            not exist.

        For example, to get the second removal reason of r/test:

        .. code-block:: python

            reason = reddit.subreddit("test").mod.removal_reasons[1]

        To get the last three removal reasons in a subreddit:

        .. code-block:: python

            reasons = reddit.subreddit("test").mod.removal_reasons[-3:]
            for reason in reasons:
                print(reason)

        """
        if not isinstance(reason_id, str):
            return self._removal_reason_list[reason_id]
        return RemovalReason(self._reddit, self.subreddit, reason_id)

    def __init__(self, subreddit: praw.models.Subreddit) -> None:
        """Initialize a :class:`.SubredditRemovalReasons` instance.

        :param subreddit: The subreddit whose removal reasons to work with.

        """
        self.subreddit = subreddit
        self._reddit = subreddit._reddit

    def __iter__(self) -> Iterator[RemovalReason]:
        """Return a list of Removal Reasons for the subreddit.

        This method is used to discover all removal reasons for a subreddit:

        .. code-block:: python

            for removal_reason in reddit.subreddit("test").mod.removal_reasons:
                print(removal_reason)

        """
        return iter(self._removal_reason_list)

    def add(self, *, message: str, title: str) -> RemovalReason:
        """Add a removal reason to this subreddit.

        :param message: The message associated with the removal reason.
        :param title: The title of the removal reason.

        :returns: The :class:`.RemovalReason` added.

        The message will be prepended with ``Hi u/username,`` automatically.

        To add ``"Test"`` to r/test try:

        .. code-block:: python

            reddit.subreddit("test").mod.removal_reasons.add(title="Test", message="Foobar")

        """
        data = {"message": message, "title": title}
        url = API_PATH["removal_reasons_list"].format(subreddit=self.subreddit)
        reason_id = self._reddit.post(url, data=data)
        return RemovalReason(self._reddit, self.subreddit, reason_id)
