from ..redditmodel import RedditModel


class Savable(RedditModel):
    """Interface for RedditContentObjects that can be saved."""

    def save(self, unsave=False):
        """Save the object.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['unsave' if unsave else 'save']
        data = {'id': self.fullname,
                'executed': 'unsaved' if unsave else 'saved'}
        return self.reddit_session.request_json(url, data=data)

    def unsave(self):
        """Unsave the object.

        :returns: The json response from the server.

        """
        return self.save(unsave=True)
