"""Provide the ReplyableMixin class."""
from ....const import API_PATH


class ReplyableMixin:
    """Interface for RedditBase classes that can be replied to."""

    def reply(self, body):
        """Reply to the object.

        :param body: The markdown formatted content for a comment.
        :returns: :class:`~.Comment` if the target is a comment,
            :class:`~.Message` if the target is a message, or ``None``
            if Reddit doesn't return any context.

        A ``None`` value may be returned if the target is a comment or
        submission in a quarantined subreddit and the authenticated user
        is not opt-ed in to viewing the content. When this happens the
        comment will be sucessfully created on Reddit and can be retrieved
        by drawing the comment from the user's comment history.

        Example usage:

        .. code:: python

           submission = reddit.submission(id='5or86n')
           submission.reply('reply')

           comment = reddit.comment(id='dxolpyc')
           comment.reply('reply')

        """
        data = {"text": body, "thing_id": self.fullname}
        response_data = self._reddit._request_and_check_error(
            "POST", API_PATH["comment"], data=data
        )

        obj = None
        things = response_data["json"]["data"]["things"]
        try:
            schema = things[0]
        except IndexError:
            return None
        if schema["kind"] == self._reddit.config.kinds["comment"]:
            obj = self._reddit._objector.parsers[
                self._reddit.config.kinds["comment"]
            ](self._reddit, _data=schema["data"])
        elif schema["kind"] == self._reddit.config.kinds["message"]:
            obj = self._reddit._objector.parsers[
                self._reddit.config.kinds["message"]
            ](self._reddit, _data=schema["data"])
        return obj
