"""Provides the User class."""
from ..const import API_PATH
from .base import PRAWBase
from .reddit.redditor import Redditor


class User(PRAWBase):
    """The user class provides methods for the currently authenticated user."""

    def friends(self):
        """Return a RedditList of friends."""
        return self._reddit.get(API_PATH['friends'])

    def me(self):  # pylint: disable=invalid-name
        """Return a Redditor instance for the authenticated user."""
        user_data = self._reddit.get(API_PATH['me'])
        return Redditor(self, _data=user_data)
