"""Provide the InboxableMixin class."""


class InboxableMixin(object):
    """Interface for RedditBase classes that originate from the inbox."""

    def mark_read(self):
        """Mark item as read."""
        self._reddit.inbox.mark_read([self])

    def mark_unread(self):
        """Mark item as unread."""
        self._reddit.inbox.mark_unread([self])
