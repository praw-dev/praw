"""Provide the ReplyableMixin class."""
from ....const import API_PATH
from ...util import stream_generator


class ReplyableMixin:
    """Interface for RedditBase classes that can be replied to."""

    def comment_stream(self, **stream_options):
        """Create a stream yielding new top-level comments/comment replies.

        :param stream_options: Options to pass to :func:`.stream_generator`.
        :returns: A stream for top-level comments.

        Example usage:

        .. code-block:: python

            submission = reddit.submission(id='5or86n')
            for comment in submission.comment_stream():
                print(comment)


            parent_comment = reddit.comment(id='dxolpyc')
            for comment in parent_comment.comment_stream():
                print(comment)
        """
        forest = self.comments if "comments" in dir(self) else self.replies
        return stream_generator(
            forest.tree,
            exclude_before=True,
            showmore=False,
            sort="new",
            context=0,
            depth=0,
            threaded=False,
            **stream_options
        )

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

        .. note:: Some items, such as locked submissions/comments or
            non-replyable messages will throw ``prawcore.exceptions.Forbidden``
            when attempting to reply to them.

        Example usage:

        .. code-block:: python

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
