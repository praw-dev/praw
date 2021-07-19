"""Provide the MessageableMixin class."""
from typing import TYPE_CHECKING, Optional, Union

from ....const import API_PATH

if TYPE_CHECKING:  # pragma: no cover
    import praw


class MessageableMixin:
    """Interface for classes that can be messaged."""

    def message(
        self,
        subject: str,
        message: str,
        from_subreddit: Optional[Union["praw.models.Subreddit", str]] = None,
    ):
        """Send a message to a redditor or a subreddit's moderators (mod mail).

        :param subject: The subject of the message.
        :param message: The message content.
        :param from_subreddit: A :class:`~.Subreddit` instance or string to send the
            message from. When provided, messages are sent from the subreddit rather
            than from the authenticated user.

            .. note::

                The authenticated user must be a moderator of the subreddit and have the
                ``mail`` moderator permission.


        For example, to send a private message to ``u/spez``, try:

        .. code-block:: python

            reddit.redditor("spez").message("TEST", "test message from PRAW")

        To send a message to ``u/spez`` from the moderators of ``r/test`` try:

        .. code-block:: python

            reddit.redditor("spez").message(
                "TEST", "test message from r/test", from_subreddit="test"
            )

        To send a message to the moderators of ``r/test``, try:

        .. code-block:: python

            reddit.subreddit("test").message("TEST", "test PM from PRAW")

        """
        data = {
            "subject": subject,
            "text": message,
            "to": f"{getattr(self.__class__, 'MESSAGE_PREFIX', '')}{self}",
        }
        if from_subreddit:
            data["from_sr"] = str(from_subreddit)
        self._reddit.post(API_PATH["compose"], data=data)
