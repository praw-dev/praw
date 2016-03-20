"""Provide the SavableMixin class."""


class SavableMixin(object):
    """Interface for RedditBase classes that can be saved."""

    def save(self, unsave=False):
        """Save the object.

        :returns: The json response from the server.

        """
        url = self._reddit.config['unsave' if unsave else 'save']
        data = {'id': self.fullname,
                'executed': 'unsaved' if unsave else 'saved'}
        return self._reddit.post(url, data=data)

    def unsave(self):
        """Unsave the object.

        :returns: The json response from the server.

        """
        return self.save(unsave=True)
