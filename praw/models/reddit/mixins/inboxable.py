"""Provide the InboxableMixin class."""


class InboxableMixin(object):
    """Interface for RedditBase classes that originate from the inbox."""

    def mark_as_read(self):
        """Mark object as read.

        :returns: The json response from the server.

        """
        return self.reddit_session._mark_as_read([self.fullname])

    def mark_as_unread(self):
        """Mark object as unread.

        :returns: The json response from the server.

        """
        return self.reddit_session._mark_as_read([self.fullname], unread=True)
