"""Provide the InboxableMixin class."""

from ....const import API_PATH


class InboxableMixin(object):
    """Interface for RedditBase classes that originate from the inbox."""

    def block(self):
        """Block the user who sent the item."""
        self._reddit.post(API_PATH['block'], data={'id': self.fullname})

    def collapse(self):
        """Mark the item as collapsed.

        .. note:: This method pertains only to objects which were retrieved via
                  the inbox.

        """
        self._reddit.inbox.collapse([self])

    def mark_read(self):
        """Mark the item as read.

        .. note:: This method pertains only to objects which were retrieved via
                  the inbox.

        """
        self._reddit.inbox.mark_read([self])

    def mark_unread(self):
        """Mark the item as unread.

        .. note:: This method pertains only to objects which were retrieved via
                  the inbox.

        """
        self._reddit.inbox.mark_unread([self])

    def uncollapse(self):
        """Mark the item as uncollapsed.

        .. note:: This method pertains only to objects which were retrieved via
                  the inbox.

        """
        self._reddit.inbox.uncollapse([self])
