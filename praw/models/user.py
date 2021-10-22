"""Provides the User class."""
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Union
from warnings import warn

from prawcore import BadRequest, Conflict

from ..const import API_PATH
from ..exceptions import ReadOnlyException
from ..models import Preferences
from ..util.cache import cachedproperty
from .base import PRAWBase
from .listing.generator import ListingGenerator
from .reddit.redditor import Redditor
from .reddit.subreddit import Subreddit

if TYPE_CHECKING:  # pragma: no cover
    import praw


class User(PRAWBase):
    """The user class provides methods for the currently authenticated user."""

    @cachedproperty
    def preferences(self) -> "praw.models.Preferences":
        """Get an instance of :class:`~.Preferences`.

        The preferences can be accessed as a ``dict`` like so:

        .. code-block:: python

            preferences = reddit.user.preferences()
            print(preferences["show_link_flair"])

        Preferences can be updated via:

        .. code-block:: python

            reddit.user.preferences.update(show_link_flair=True)

        The :meth:`.Preferences.update` method returns the new state of the preferences
        as a ``dict``, which can be used to check whether a change went through. Changes
        with invalid types or parameter names fail silently.

        .. code-block:: python

            original_preferences = reddit.user.preferences()
            new_preferences = reddit.user.preferences.update(invalid_param=123)
            print(original_preferences == new_preferences)  # True, no change

        """
        return Preferences(self._reddit)

    def __init__(self, reddit: "praw.Reddit"):
        """Initialize a User instance.

        This class is intended to be interfaced with through ``reddit.user``.

        """
        super().__init__(reddit, _data=None)

    def blocked(self) -> List["praw.models.Redditor"]:
        """Return a RedditorList of blocked Redditors."""
        return self._reddit.get(API_PATH["blocked"])

    def contributor_subreddits(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator["praw.models.Subreddit"]:
        """Return a :class:`.ListingGenerator` of contributor subreddits.

        These are subreddits in which the user is an approved user.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print a list of the subreddits that you are an approved user in, try:

        .. code-block:: python

            for subreddit in reddit.user.contributor_subreddits(limit=None):
                print(str(subreddit))

        """
        return ListingGenerator(
            self._reddit, API_PATH["my_contributor"], **generator_kwargs
        )

    def friends(
        self, user: Optional[Union[str, "praw.models.Redditor"]] = None
    ) -> Union[List["praw.models.Redditor"], "praw.models.Redditor"]:
        """Return a RedditorList of friends or a Redditor in the friends list.

        :param user: Checks to see if you are friends with the Redditor. Either an
            instance of :class:`.Redditor` or a string can be given.

        :returns: A list of Redditors, or a Redditor if you are friends with the given
            Redditor. The Redditor also has friend attributes.

        :raises: An instance of :class:`.RedditAPIException` if you are not friends with
            the specified Redditor.

        """
        endpoint = (
            API_PATH["friends"]
            if user is None
            else API_PATH["friend_v1"].format(user=str(user))
        )
        return self._reddit.get(endpoint)

    def karma(self) -> Dict["praw.models.Subreddit", Dict[str, int]]:
        """Return a dictionary mapping subreddits to their karma.

        The returned dict contains subreddits as keys. Each subreddit key contains a
        sub-dict that have keys for ``comment_karma`` and ``link_karma``. The dict is
        sorted in descending karma order.

        .. note::

            Each key of the main dict is an instance of :class:`~.Subreddit`. It is
            recommended to iterate over the dict in order to retrieve the values,
            preferably through ``dict.items()``.

        """
        karma_map = {}
        for row in self._reddit.get(API_PATH["karma"])["data"]:
            subreddit = Subreddit(self._reddit, row["sr"])
            del row["sr"]
            karma_map[subreddit] = row
        return karma_map

    def me(
        self, use_cache: bool = True
    ) -> Optional["praw.models.Redditor"]:  # pylint: disable=invalid-name
        """Return a :class:`.Redditor` instance for the authenticated user.

        :param use_cache: When true, and if this function has been previously called,
            returned the cached version (default: True).

        .. note::

            If you change the Reddit instance's authorization, you might want to refresh
            the cached value. Prefer using separate Reddit instances, however, for
            distinct authorizations.

        .. deprecated:: 7.2

            In :attr:`.read_only` mode this method returns ``None``. In PRAW 8 this
            method will raise :class:`.ReadOnlyException` when called in
            :attr:`.read_only` mode. To operate in PRAW 8 mode, set the config variable
            ``praw8_raise_exception_on_me`` to ``True``.

        """
        if self._reddit.read_only:
            if not self._reddit.config.custom.get("praw8_raise_exception_on_me"):
                warn(
                    "The `None` return value is deprecated, and will raise a"
                    " `ReadOnlyException` beginning with PRAW 8. See documentation for"
                    " forward compatibility options.",
                    category=DeprecationWarning,
                    stacklevel=2,
                )
                return None
            raise ReadOnlyException("`user.me()` does not work in read_only mode")
        if "_me" not in self.__dict__ or not use_cache:
            user_data = self._reddit.get(API_PATH["me"])
            self._me = Redditor(self._reddit, _data=user_data)
        return self._me

    def moderator_subreddits(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator["praw.models.Subreddit"]:
        """Return a :class:`.ListingGenerator` subreddits that the user moderates.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print a list of the names of the subreddits you moderate, try:

        .. code-block:: python

            for subreddit in reddit.user.moderator_subreddits(limit=None):
                print(str(subreddit))

        .. seealso::

            :meth:`.Redditor.moderated`

        """
        return ListingGenerator(
            self._reddit, API_PATH["my_moderator"], **generator_kwargs
        )

    def multireddits(self) -> List["praw.models.Multireddit"]:
        """Return a list of multireddits belonging to the user."""
        return self._reddit.get(API_PATH["my_multireddits"])

    def pin(
        self, submission: "praw.models.Submission", num: int = -1, state: bool = True
    ):
        """Set the submission's sticky state on user's profile.

        :param submission: The submission that will get pinned/unpinned.
        :param num: (int) The number to specify the slot in which the submission will
            get pinned, and if there is already a submission stickied in that slot it
            will be replaced. Valid input range is from 1 to 4. If there is no post in
            the specified slot to replace, or ``num`` isn't specified the bottom-most
            slot will be used (default: -1).
        :param state: (bool) True sets the sticky for the submission, false unsets
            (default: True).

        .. note::

            When a submission is stickied two or more times, the Reddit API responds
            with a 409 error that is raises as a ``Conflict`` by prawcore. The
            submissions that have been removed by the respective subreddit moderators
            cannot be pinned, and the Reddit API responds with a 400 error that is
            raised as ``BadRequest`` by prawcore. In both cases, the method will
            suppress the exception.

        .. code-block:: python

            submission = reddit.submission(id="qc3i1n")
            reddit.user.pin(submission)

        """
        num = None if num not in range(1, 5) else num
        data = {
            "id": submission.fullname,
            "num": num,
            "state": state,
            "to_profile": True,
        }
        try:
            return self._reddit.post(API_PATH["sticky_submission"], data=data)
        except (BadRequest, Conflict):
            pass

    def subreddits(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator["praw.models.Subreddit"]:
        """Return a :class:`.ListingGenerator` of subreddits the user is subscribed to.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To print a list of the subreddits that you are subscribed to, try:

        .. code-block:: python

            for subreddit in reddit.user.subreddits(limit=None):
                print(str(subreddit))

        """
        return ListingGenerator(
            self._reddit, API_PATH["my_subreddits"], **generator_kwargs
        )

    def trusted(self) -> List["praw.models.Redditor"]:
        """Return a RedditorList of trusted Redditors.

        To display the usernames of your trusted users and the times at which you
        decided to trust them, try:

        .. code-block:: python

            trusted_users = reddit.user.trusted()
            for user in trusted_users:
                print(f"User: {user.name}, time: {user.date}")

        """
        return self._reddit.get(API_PATH["trusted"])
