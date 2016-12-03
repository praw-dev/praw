"""Provide the SavableMixin class."""
from ....const import API_PATH


class SavableMixin(object):
    """Interface for RedditBase classes that can be saved."""

    def save(self, category=None):
        """Save the object.

        :param category: (Gold) The category to save to (Default:
            None). If your user does not have gold this value is ignored by
            Reddit.

        """
        self._reddit.post(API_PATH['save'], data={'category': category,
                                                  'id': self.fullname})

    def unsave(self):
        """Unsave the object."""
        self._reddit.post(API_PATH['unsave'], data={'id': self.fullname})
