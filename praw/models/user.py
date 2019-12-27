"""Provides the User class."""
from typing import Dict, Generator, List, Optional, TypeVar, Union

from ..const import API_PATH
from ..models import Preferences
from ..util.cache import cachedproperty
from .base import PRAWBase
from .listing.generator import ListingGenerator
from .reddit.redditor import Redditor
from .reddit.subreddit import Subreddit

Multireddit = TypeVar("Multireddit")
Reddit = TypeVar("Reddit")


class User(PRAWBase):
    """The user class provides methods for the currently authenticated user."""

    @cachedproperty
    def preferences(self) -> Preferences:
        """Get an instance of :class:`.Preferences`.

        The preferences can be accessed as a ``dict`` like so:

        .. code-block:: python

           preferences = reddit.user.preferences()
           print(preferences['show_link_flair'])

        Preferences can be updated via:

        .. code-block:: python

           reddit.user.preferences.update(show_link_flair=True)

        The :meth:`.Preferences.update` method returns the new state of the
        preferences as a ``dict``, which can be used to check whether a
        change went through. Changes with invalid types or parameter names
        fail silently.

        .. code-block:: python

           original_preferences = reddit.user.preferences()
           new_preferences = reddit.user.preferences.update(invalid_param=123)
           print(original_preferences == new_preferences)  # True, no change


        """
        return Preferences(self._reddit)

    def __init__(self, reddit: Reddit):
        """Initialize a User instance.

        This class is intended to be interfaced with through ``reddit.user``.

        """
        super().__init__(reddit, _data=None)

    def blocked(self) -> List[Redditor]:
        """Return a RedditorList of blocked Redditors."""
        return self._reddit.get(API_PATH["blocked"])

    def contributor_subreddits(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Generator[Subreddit, None, None]:
        """Return a :class:`.ListingGenerator` of subreddits user is a contributor of.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit, API_PATH["my_contributor"], **generator_kwargs
        )

    def friends(self) -> List[Redditor]:
        """Return a RedditorList of friends."""
        return self._reddit.get(API_PATH["friends"])

    def karma(self) -> Dict[Subreddit, int]:
        """Return a dictionary mapping subreddits to their karma."""
        karma_map = {}
        for row in self._reddit.get(API_PATH["karma"])["data"]:
            subreddit = Subreddit(self._reddit, row["sr"])
            del row["sr"]
            karma_map[subreddit] = row
        return karma_map

    def me(
        self, use_cache: bool = True
    ) -> Optional[Redditor]:  # pylint: disable=invalid-name
        """Return a :class:`.Redditor` instance for the authenticated user.

        In :attr:`~praw.Reddit.read_only` mode, this method returns ``None``.

        :param use_cache: When true, and if this function has been previously
            called, returned the cached version (default: True).

        .. note:: If you change the Reddit instance's authorization, you might
           want to refresh the cached value. Prefer using separate Reddit
           instances, however, for distinct authorizations.

        """
        if self._reddit.read_only:
            return None
        if "_me" not in self.__dict__ or not use_cache:
            user_data = self._reddit.get(API_PATH["me"])
            self._me = Redditor(self._reddit, _data=user_data)
        return self._me

    def moderator_subreddits(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Generator[Subreddit, None, None]:
        """Return a :class:`.ListingGenerator` of moderated subreddits.

        ..warning:: (Deprecated) This method will be removed in the next major
                    version of PRAW. Please use :meth:`.Redditor.moderated`
                    instead.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        .. note:: This method will return a maximum of 100 moderated
           subreddits, ordered by subscriber count. To retrieve more than
           100 moderated subreddits, please see :meth:`.Redditor.moderated`.

        Usage:

        .. code-block:: python

           for subreddit in reddit.user.moderator_subreddits():
               print(subreddit.display_name)


        """
        return ListingGenerator(
            self._reddit, API_PATH["my_moderator"], **generator_kwargs
        )

    def multireddits(self) -> List[Multireddit]:
        """Return a list of multireddits belonging to the user."""
        return self._reddit.get(API_PATH["my_multireddits"])

    def subreddits(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Generator[Subreddit, None, None]:
        """Return a :class:`.ListingGenerator` of subreddits the user is subscribed to.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        return ListingGenerator(
            self._reddit, API_PATH["my_subreddits"], **generator_kwargs
        )
