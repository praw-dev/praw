from ..redditmodel import RedditModel


class Inboxable(RedditModel):
    """Interface for objects that appear in the inbox (orangereds)."""

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

    def reply(self, text):
        """Reply to object with the specified text.

        :returns: A Comment object for the newly created comment (reply).

        """
        return self.reddit_session._add_comment(self.fullname, text)
