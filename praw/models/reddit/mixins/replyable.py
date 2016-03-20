"""Provide the ReplyableMixin class."""
from ....const import API_PATH


class ReplyableMixin(object):
    """Interface for RedditBase classes that can be replied to."""

    def reply(self, text):
        """Reply to the object..

        :returns: A :class:`~.Comment` object for the newly created comment.

        """
        data = {'thing_id': self.fullname, 'text': text}
        return self._reddit.post(API_PATH['comment'], data=data)[0]
