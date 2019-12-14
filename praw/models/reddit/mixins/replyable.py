"""Provide the ReplyableMixin class."""
from ....const import API_PATH


class ReplyableMixin:
    """Interface for RedditBase classes that can be replied to."""

    def reply(self, body):
        """Reply to the object.

        :param body: The Markdown formatted content for a comment.
        :returns: A :class:`~.Comment` object for the newly created
            comment or ``None`` if Reddit doesn't provide one.

        A ``None`` value can be returned if the target is a comment or
        submission in a quarantined subreddit and the authenticated user
        has not opt-ed in to viewing the content. When this happens the
        comment will be sucessfully created on Reddit and can be retried
        by drawing the comment from the user's comment history.

        Example usage:

        .. code:: python

           submission = reddit.submission(id='5or86n')
           submission.reply('reply')

           comment = reddit.comment(id='dxolpyc')
           comment.reply('reply')

        """
        data = {"text": body, "thing_id": self.fullname}
        comments = self._reddit.post(API_PATH["comment"], data=data)
        try:
            return comments[0]
        except IndexError:
            return None
