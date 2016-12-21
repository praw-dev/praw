"""Provide the ReplyableMixin class."""
from ....const import API_PATH


class ReplyableMixin(object):
    """Interface for RedditBase classes that can be replied to."""

    def reply(self, body):
        """Reply to the object.

        :param body: The markdown formatted content for a comment.
        :returns: A :class:`~.Comment` object for the newly created comment.

        """
        data = {'text': body, 'thing_id': self.fullname}
        return self._reddit.post(API_PATH['comment'], data=data)[0]
