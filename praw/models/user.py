"""Provides the User class."""
from ..const import API_PATH
from .base import PRAWBase
from .listing.generator import ListingGenerator
from .reddit.redditor import Redditor
from .reddit.subreddit import Subreddit


class User(PRAWBase):
    """The user class provides methods for the currently authenticated user."""

    def blocked(self):
        """Return a RedditorList of blocked Redditors."""
        return self._reddit.get(API_PATH['blocked'])

    def contributor_subreddits(self, **generator_kwargs):
        """Return a ListingGenerator of subreddits user is a contributor of.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, API_PATH['my_contributor'],
                                **generator_kwargs)

    def friends(self):
        """Return a RedditorList of friends."""
        return self._reddit.get(API_PATH['friends'])

    def karma(self):
        """Return a dictionary mapping subreddits to their karma."""
        karma_map = {}
        for row in self._reddit.get(API_PATH['karma'])['data']:
            subreddit = Subreddit(self._reddit, row['sr'])
            del row['sr']
            karma_map[subreddit] = row
        return karma_map

    def me(self):  # pylint: disable=invalid-name
        """Return a Redditor instance for the authenticated user."""
        user_data = self._reddit.get(API_PATH['me'])
        return Redditor(self._reddit, _data=user_data)

    def moderator_subreddits(self, **generator_kwargs):
        """Return a ListingGenerator of subreddits the user is a moderator of.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, API_PATH['my_moderator'],
                                **generator_kwargs)

    def multireddits(self):
        """Return a list of multireddits belonging to the user."""
        return self._reddit.get(API_PATH['my_multireddits'])

    def subreddits(self, **generator_kwargs):
        """Return a ListingGenerator of subreddits the user is subscribed to.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, API_PATH['my_subreddits'],
                                **generator_kwargs)
