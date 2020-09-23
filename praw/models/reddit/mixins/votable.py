"""Provide the VotableMixin class."""
from ....const import API_PATH


class VotableMixin:
    """Interface for RedditBase classes that can be voted on."""

    def _vote(self, direction: int):
        self._reddit.post(
            API_PATH["vote"], data={"dir": str(direction), "id": self.fullname}
        )

    def clear_vote(self):
        """Clear the authenticated user's vote on the object.

        .. note::

            Votes must be cast by humans. That is, API clients proxying a human's action
            one-for-one are OK, but bots deciding how to vote on content or amplifying a
            human's vote are not. See the reddit rules for more details on what
            constitutes vote cheating. [`Ref
            <https://www.reddit.com/dev/api#POST_api_vote>`_]

        Example usage:

        .. code-block:: python

            submission = reddit.submission(id="5or86n")
            submission.clear_vote()

            comment = reddit.comment(id="dxolpyc")
            comment.clear_vote()

        """
        self._vote(direction=0)

    def downvote(self):
        """Downvote the object.

        .. note::

            Votes must be cast by humans. That is, API clients proxying a human's action
            one-for-one are OK, but bots deciding how to vote on content or amplifying a
            human's vote are not. See the reddit rules for more details on what
            constitutes vote cheating. [`Ref
            <https://www.reddit.com/dev/api#POST_api_vote>`_]

        Example usage:

        .. code-block:: python

            submission = reddit.submission(id="5or86n")
            submission.downvote()

            comment = reddit.comment(id="dxolpyc")
            comment.downvote()

        .. seealso::

            :meth:`~.upvote`

        """
        self._vote(direction=-1)

    def upvote(self):
        """Upvote the object.

        .. note::

            Votes must be cast by humans. That is, API clients proxying a human's action
            one-for-one are OK, but bots deciding how to vote on content or amplifying a
            human's vote are not. See the reddit rules for more details on what
            constitutes vote cheating. [`Ref
            <https://www.reddit.com/dev/api#POST_api_vote>`_]

        Example usage:

        .. code-block:: python

            submission = reddit.submission(id="5or86n")
            submission.upvote()

            comment = reddit.comment(id="dxolpyc")
            comment.upvote()

        .. seealso::

            :meth:`~.downvote`

        """
        self._vote(direction=1)
