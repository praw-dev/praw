"""Provide the InboxableMixin class."""

from ....const import API_PATH


class InboxableMixin:
    """Interface for RedditBase classes that originate from the inbox."""

    def block(self):
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

    def collapse(self):
        """Mark the item as collapsed.

        This method pertains only to objects which were retrieved via the inbox.

        Example usage:

        .. code-block:: python

            inbox = reddit.inbox()

            # select first inbox item and collapse it message = next(inbox)
            message.collapse()

        .. seealso::

            :meth:`~.uncollapse`

        """
        self._reddit.inbox.collapse([self])

    def mark_read(self):
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

            :meth:`~.mark_unread`

        To mark the whole inbox as read with a single network request, use
        :meth:`praw.models.Inbox.mark_read`

        """
        self._reddit.inbox.mark_read([self])

    def mark_unread(self):
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

            :meth:`~.mark_read`

        """
        self._reddit.inbox.mark_unread([self])

    def uncollapse(self):
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

            :meth:`~.collapse`

        """
        self._reddit.inbox.uncollapse([self])
