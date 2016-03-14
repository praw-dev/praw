"""Provide the VotableMixin class."""
from six import text_type


class VotableMixin(object):
    """Interface for classes that can be voted on."""

    def clear_vote(self):
        """Remove the logged in user's vote on the object.

        Running this on an object with no existing vote has no adverse effects.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        :returns: The json response from the server.

        """
        return self.vote()

    def downvote(self):
        """Downvote object. If there already is a vote, replace it.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        :returns: The json response from the server.

        """
        return self.vote(direction=-1)

    def upvote(self):
        """Upvote object. If there already is a vote, replace it.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        :returns: The json response from the server.

        """
        return self.vote(direction=1)

    def vote(self, direction=0):
        """Vote for the given item in the direction specified.

        Note: votes must be cast by humans. That is, API clients proxying a
        human's action one-for-one are OK, but bots deciding how to vote on
        content or amplifying a human's vote are not. See the reddit rules for
        more details on what constitutes vote cheating.

        Source for note: http://www.reddit.com/dev/api#POST_api_vote

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['vote']
        data = {'id': self.fullname, 'dir': text_type(direction)}
        return self.core.request_json(url, data=data)
