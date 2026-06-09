"""Provide the InboxToggleableMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from praw.const import API_PATH

if TYPE_CHECKING:
    import praw


class InboxToggleableMixin:
    """Interface for classes that can optionally receive inbox replies."""

    if TYPE_CHECKING:
        # Provided by the host class (:class:`.RedditBase`).
        _reddit: praw.Reddit

        @property
        def fullname(self) -> str: ...  # noqa: D102

    def disable_inbox_replies(self) -> None:
        """Disable inbox replies for the item.

        .. note::

            This can only apply to items created by the authenticated user.

        Example usage:

        .. code-block:: python

            comment = reddit.comment("dkk4qjd")
            comment.disable_inbox_replies()

            submission = reddit.submission("8dmv8z")
            submission.disable_inbox_replies()

        .. seealso::

            :meth:`.enable_inbox_replies`

        """
        self._reddit.post(API_PATH["sendreplies"], data={"id": self.fullname, "state": False})

    def enable_inbox_replies(self) -> None:
        """Enable inbox replies for the item.

        .. note::

            This can only apply to items created by the authenticated user.

        Example usage:

        .. code-block:: python

            comment = reddit.comment("dkk4qjd")
            comment.enable_inbox_replies()

            submission = reddit.submission("8dmv8z")
            submission.enable_inbox_replies()

        .. seealso::

            :meth:`.disable_inbox_replies`

        """
        self._reddit.post(API_PATH["sendreplies"], data={"id": self.fullname, "state": True})
