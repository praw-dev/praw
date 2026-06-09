"""Provide the InboxableMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from praw.const import API_PATH

if TYPE_CHECKING:
    import praw
    from praw import models


class InboxableMixin:
    """Interface for :class:`.RedditBase` subclasses that originate from the inbox."""

    if TYPE_CHECKING:
        # Provided by the host class (:class:`.RedditBase`).
        _reddit: praw.Reddit

        @property
        def fullname(self) -> str: ...  # noqa: D102

    def block(self) -> None:
        """Block the user who sent the item.

        .. note::

            This method pertains only to objects which were retrieved via the inbox.

        Example usage:

        .. code-block:: python

            comment = reddit.comment("dkk4qjd")
            comment.block()

            # or, identically:

            comment.author.block()

        """
        self._reddit.post(API_PATH["block"], data={"id": self.fullname})

    def collapse(self) -> None:
        """Mark the item as collapsed.

        .. note::

            This method pertains only to objects which were retrieved via the inbox.

        Example usage:

        .. code-block:: python

            inbox = reddit.inbox()

            # select first inbox item and collapse it message = next(inbox)
            message.collapse()

        .. seealso::

            :meth:`.uncollapse`

        """
        self._reddit.inbox.collapse([cast("models.Message", self)])

    def mark_read(self) -> None:
        """Mark a single inbox item as read.

        .. note::

            This method pertains only to objects which were retrieved via the inbox.

        Example usage:

        .. code-block:: python

            inbox = reddit.inbox.unread()

            for message in inbox:
                # process unread messages
                ...

        .. seealso::

            :meth:`.mark_unread`

        To mark the whole inbox as read with a single network request, use
        :meth:`.Inbox.mark_all_read`

        """
        self._reddit.inbox.mark_read([cast("models.Comment | models.Message", self)])

    def mark_unread(self) -> None:
        """Mark the item as unread.

        .. note::

            This method pertains only to objects which were retrieved via the inbox.

        Example usage:

        .. code-block:: python

            inbox = reddit.inbox(limit=10)

            for message in inbox:
                # process messages
                ...

        .. seealso::

            :meth:`.mark_read`

        """
        self._reddit.inbox.mark_unread([cast("models.Comment | models.Message", self)])

    def uncollapse(self) -> None:
        """Mark the item as uncollapsed.

        .. note::

            This method pertains only to objects which were retrieved via the inbox.

        Example usage:

        .. code-block:: python

            inbox = reddit.inbox()

            # select first inbox item and uncollapse it
            message = next(inbox)
            message.uncollapse()

        .. seealso::

            :meth:`.collapse`

        """
        self._reddit.inbox.uncollapse([cast("models.Message", self)])
