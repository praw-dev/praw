"""Provide the VotableMixin class."""
from ....const import API_PATH


class VotableMixin(object):
    """Interface for RedditBase classes that can be voted on."""

    def clear_vote(self):
        """Clear the authenticated user's vote on the object.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        """
        self.vote(direction=0)

    def downvote(self):
        """Downvote the object.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        """
        self.vote(direction=-1)

    def upvote(self):
        """Upvote the object.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        """
        self.vote(direction=1)

    def vote(self, direction):
        """Vote on the object in the direction specified.

        :param direction: The direction to vote in with -1 being down; 0,
        clear; and 1, up.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        """
        self._reddit.post(API_PATH['vote'], data={'dir': str(direction),
                                                  'id': self.fullname})
