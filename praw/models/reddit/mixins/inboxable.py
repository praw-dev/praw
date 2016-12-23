"""Provide the InboxableMixin class."""

from ....const import API_PATH


class InboxableMixin(object):
    """Interface for RedditBase classes that originate from the inbox."""

    def block(self):
        """Block the user who sent the item.

        :returns: The json response from the server.

        .. note:: Reddit does not permit blocking users unless you have a
                  :class:`.Comment` or :class:`.Message` from them.

        """
        return self._reddit.post(API_PATH['block'], data={'id': self.fullname})

    def mark_read(self):
        """Mark the item as read."""
        self._reddit.inbox.mark_read([self])

    def mark_unread(self):
        """Mark the item as unread."""
        self._reddit.inbox.mark_unread([self])
