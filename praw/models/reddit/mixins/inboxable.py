"""Provide the InboxableMixin class."""

from ....const import API_PATH


class InboxableMixin(object):
    """Interface for RedditBase classes that originate from the inbox."""

    def block(self):
        """Block the user who sent the item.

        Example usage:

        .. code:: python

           comment = reddit.comment('dkk4qjd')
           comment.block()

           # or, identically:

           comment.author.block()

        """
        self._reddit.post(API_PATH['block'], data={'id': self.fullname})

    def collapse(self):
        """Mark the item as collapsed.

        .. note:: This method pertains only to objects which were retrieved via
                  the inbox.

        Example usage:

        .. code:: python

           inbox = reddit.inbox()

           # select first inbox item and collapse it
           message = list(inbox)[0]
           message.collapse()

        See also :meth:`~.uncollapse`

        """
        self._reddit.inbox.collapse([self])

    def mark_read(self):
        """Mark the item as read.

        .. note:: This method pertains only to objects which were retrieved via
                  the inbox.

        Example usage:

        .. code:: python

           inbox = reddit.inbox.unread()

           # mark all unread inbox items as read
           for message in inbox:
               message.mark_read()

        See also :meth:`~.mark_unread`

        """
        self._reddit.inbox.mark_read([self])

    def mark_unread(self):
        """Mark the item as unread.

        .. note:: This method pertains only to objects which were retrieved via
                  the inbox.

        Example usage:

        .. code:: python

           inbox = reddit.inbox(limit=5)

           # mark last 5 inbox items as unread
           for message in inbox:
               message.mark_unread()

        See also :meth:`~.mark_read`

        """
        self._reddit.inbox.mark_unread([self])

    def uncollapse(self):
        """Mark the item as uncollapsed.

        .. note:: This method pertains only to objects which were retrieved via
                  the inbox.

        Example usage:

        .. code:: python

           inbox = reddit.inbox()

           # select first inbox item and uncollapse it
           message = list(inbox)[0]
           message.uncollapse()

        See also :meth:`~.uncollapse`

        """
        self._reddit.inbox.uncollapse([self])
