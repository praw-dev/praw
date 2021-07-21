"""Provide the Redditor class."""
from json import dumps
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Union

from ...const import API_PATH
from ...util.cache import cachedproperty
from ..listing.mixins import RedditorListingMixin
from ..util import stream_generator
from .base import RedditBase
from .mixins import FullnameMixin, MessageableMixin

if TYPE_CHECKING:  # pragma: no cover
    import praw


class Redditor(MessageableMixin, RedditorListingMixin, FullnameMixin, RedditBase):
    """A class representing the users of reddit.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this class.
    Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a guarantee that
    these attributes will always be present, nor is this list necessarily complete.

    .. note::

        Shadowbanned accounts are treated the same as non-existent accounts, meaning
        that they will not have any attributes.

    .. note::

        Suspended/banned accounts will only return the ``name`` and ``is_suspended``
        attributes.

    =================================== ================================================
    Attribute                           Description
    =================================== ================================================
    ``comment_karma``                   The comment karma for the Redditor.
    ``comments``                        Provide an instance of :class:`.SubListing` for
                                        comment access.
    ``submissions``                     Provide an instance of :class:`.SubListing` for
                                        submission access.
    ``created_utc``                     Time the account was created, represented in
                                        `Unix Time`_.
    ``has_verified_email``              Whether or not the Redditor has verified their
                                        email.
    ``icon_img``                        The url of the Redditors' avatar.
    ``id``                              The ID of the Redditor.
    ``is_employee``                     Whether or not the Redditor is a Reddit
                                        employee.
    ``is_friend``                       Whether or not the Redditor is friends with the
                                        authenticated user.
    ``is_mod``                          Whether or not the Redditor mods any subreddits.
    ``is_gold``                         Whether or not the Redditor has active Reddit
                                        Premium status.
    ``is_suspended``                    Whether or not the Redditor is currently
                                        suspended.
    ``link_karma``                      The link karma for the Redditor.
    ``name``                            The Redditor's username.
    ``subreddit``                       If the Redditor has created a user-subreddit,
                                        provides a dictionary of additional attributes.
                                        See below.
    ``subreddit["banner_img"]``         The URL of the user-subreddit banner.
    ``subreddit["name"]``               The fullname of the user-subreddit.
    ``subreddit["over_18"]``            Whether or not the user-subreddit is NSFW.
    ``subreddit["public_description"]`` The public description of the user-subreddit.
    ``subreddit["subscribers"]``        The number of users subscribed to the
                                        user-subreddit.
    ``subreddit["title"]``              The title of the user-subreddit.
    =================================== ================================================

    .. _unix time: https://en.wikipedia.org/wiki/Unix_time

    """

    STR_FIELD = "name"

    @classmethod
    def from_data(cls, reddit, data):
        """Return an instance of Redditor, or None from ``data``."""
        if data == "[deleted]":
            return None
        return cls(reddit, data)

    @cachedproperty
    def stream(self) -> "praw.models.reddit.redditor.RedditorStream":
        """Provide an instance of :class:`.RedditorStream`.

        Streams can be used to indefinitely retrieve new comments made by a redditor,
        like:

        .. code-block:: python

            for comment in reddit.redditor("spez").stream.comments():
                print(comment)

        Additionally, new submissions can be retrieved via the stream. In the following
        example all submissions are fetched via the redditor ``spez``:

        .. code-block:: python

            for submission in reddit.redditor("spez").stream.submissions():
                print(submission)

        """
        return RedditorStream(self)

    @property
    def _kind(self) -> str:
        """Return the class's kind."""
        return self._reddit.config.kinds["redditor"]

    @property
    def _path(self) -> str:
        return API_PATH["user"].format(user=self)

    def __init__(
        self,
        reddit: "praw.Reddit",
        name: Optional[str] = None,
        fullname: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a Redditor instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param name: The name of the redditor.
        :param fullname: The fullname of the redditor, starting with ``t2_``.

        Exactly one of ``name``, ``fullname`` or ``_data`` must be provided.

        """
        if (name, fullname, _data).count(None) != 2:
            raise TypeError(
                "Exactly one of `name`, `fullname`, or `_data` must be provided."
            )
        if _data:
            assert (
                isinstance(_data, dict) and "name" in _data
            ), "Please file a bug with PRAW."
        self._listing_use_sort = True
        if name:
            self.name = name
        elif fullname:
            self._fullname = fullname
        super().__init__(reddit, _data=_data, _extra_attribute_to_check="_fullname")

    def __setattr__(self, name: str, value: Any):
        """Objectify the subreddit attribute."""
        if name == "subreddit" and value:
            from .user_subreddit import UserSubreddit

            value = UserSubreddit(reddit=self._reddit, _data=value)
        super().__setattr__(name, value)

    def _fetch_username(self, fullname):
        return self._reddit.get(API_PATH["user_by_fullname"], params={"ids": fullname})[
            fullname
        ]["name"]

    def _fetch_info(self):
        if hasattr(self, "_fullname"):
            self.name = self._fetch_username(self._fullname)
        return "user_about", {"user": self.name}, None

    def _fetch_data(self):
        name, fields, params = self._fetch_info()
        path = API_PATH[name].format(**fields)
        return self._reddit.request("GET", path, params)

    def _fetch(self):
        data = self._fetch_data()
        data = data["data"]
        other = type(self)(self._reddit, _data=data)
        self.__dict__.update(other.__dict__)
        self._fetched = True

    def _friend(self, method, data):
        url = API_PATH["friend_v1"].format(user=self)
        self._reddit.request(method, url, data=dumps(data))

    def block(self):
        """Block the Redditor.

        For example, to block Redditor ``spez``:

        .. code-block:: python

            reddit.redditor("spez").block()

        .. note::

            Blocking a trusted user will remove that user from your trusted list.

        .. seealso::

            :meth:`.trust`

        """
        self._reddit.post(API_PATH["block_user"], params={"name": self.name})

    def distrust(self):
        """Remove the Redditor from your whitelist of trusted users.

        For example, to remove Redditor ``spez`` from your whitelist:

        .. code-block:: python

            reddit.redditor("spez").distrust()

        .. seealso::

            :meth:`.trust`

        """
        self._reddit.post(API_PATH["remove_whitelisted"], data={"name": self.name})

    def friend(self, note: str = None):
        """Friend the Redditor.

        :param note: A note to save along with the relationship. Requires Reddit Premium
            (default: None).

        Calling this method subsequent times will update the note.

        For example, to friend Redditor ``spez``:

        .. code-block:: python

            reddit.redditor("spez").friend()

        To add a note to the friendship (requires Reddit Premium):

        .. code-block:: python

            reddit.redditor("spez").friend(note="My favorite admin")

        """
        self._friend("PUT", data={"note": note} if note else {})

    def friend_info(self) -> "praw.models.Redditor":
        """Return a Redditor instance with specific friend-related attributes.

        :returns: A :class:`.Redditor` instance with fields ``date``, ``id``, and
            possibly ``note`` if the authenticated user has Reddit Premium.

        For example, to get the friendship information of Redditor ``spez``:

        .. code-block:: python

            info = reddit.redditor("spez").friend_info
            friend_data = info.date

        """
        return self._reddit.get(API_PATH["friend_v1"].format(user=self))

    def gild(self, months: int = 1):
        """Gild the Redditor.

        :param months: Specifies the number of months to gild up to 36 (default: 1).

        For example, to gild Redditor ``spez`` for 1 month:

        .. code-block:: python

            reddit.redditor("spez").gild(months=1)

        """
        if months < 1 or months > 36:
            raise TypeError("months must be between 1 and 36")
        self._reddit.post(
            API_PATH["gild_user"].format(username=self),
            data={"months": months},
        )

    def moderated(self) -> List["praw.models.Subreddit"]:
        """Return a list of the redditor's moderated subreddits.

        :returns: A ``list`` of :class:`~.Subreddit` objects. Return ``[]`` if the
            redditor has no moderated subreddits.

        :raises: ``prawcore.ServerError`` in certain cicumstances. See the note below.

        .. note::

            The redditor's own user profile subreddit will not be returned, but other
            user profile subreddits they moderate will be returned.

        Usage:

        .. code-block:: python

            for subreddit in reddit.redditor("spez").moderated():
                print(subreddit.display_name)
                print(subreddit.title)

        .. note::

            A ``prawcore.ServerError`` exception may be raised if the redditor moderates
            a large number of subreddits. If that happens, try switching to
            :ref:`read-only mode <read_only_application>`. For example,

            .. code-block:: python

                reddit.read_only = True
                for subreddit in reddit.redditor("reddit").moderated():
                    print(str(subreddit))

            It is possible that requests made in read-only mode will also raise a
            ``prawcore.ServerError`` exception.

            When used in read-only mode, this method does not retrieve information about
            subreddits that require certain special permissions to access, e.g., private
            subreddits and premium-only subreddits.

        .. seealso::

            :meth:`.User.moderator_subreddits`

        """
        return self._reddit.get(API_PATH["moderated"].format(user=self)) or []

    def multireddits(self) -> List["praw.models.Multireddit"]:
        """Return a list of the redditor's public multireddits.

        For example, to to get Redditor ``spez``'s multireddits:

        .. code-block:: python

            multireddits = reddit.redditor("spez").multireddits()

        """
        return self._reddit.get(API_PATH["multireddit_user"].format(user=self))

    def trophies(self) -> List["praw.models.Trophy"]:
        """Return a list of the redditor's trophies.

        :returns: A ``list`` of :class:`.Trophy` objects. Return an empty list (``[]``)
            if the redditor has no trophies.

        :raises: :class:`.RedditAPIException` if the redditor doesn't exist.

        Usage:

        .. code-block:: python

            for trophy in reddit.redditor("spez").trophies():
                print(trophy.name)
                print(trophy.description)

        """
        return list(self._reddit.get(API_PATH["trophies"].format(user=self)))

    def trust(self):
        """Add the Redditor to your whitelist of trusted users.

        Trusted users will always be able to send you PMs.

        Example usage:

        .. code-block:: python

            reddit.redditor("AaronSw").trust()

        Use the ``accept_pms`` parameter of :meth:`.Preferences.update` to toggle your
        ``accept_pms`` setting between ``"everyone"`` and ``"whitelisted"``. For
        example:

        .. code-block:: python

            # Accept private messages from everyone:
            reddit.user.preferences.update(accept_pms="everyone")
            # Only accept private messages from trusted users:
            reddit.user.preferences.update(accept_pms="whitelisted")

        You may trust a user even if your ``accept_pms`` setting is switched to
        ``"everyone"``.

        .. note::

            You are allowed to have a user on your blocked list and your friends list at
            the same time. However, you cannot trust a user who is on your blocked list.

        .. seealso::

            - :meth:`.distrust`
            - :meth:`.Preferences.update`
            - :meth:`.trusted`

        """
        self._reddit.post(API_PATH["add_whitelisted"], data={"name": self.name})

    def unblock(self):
        """Unblock the Redditor.

        For example, to unblock Redditor ``spez``:

        .. code-block:: python

            reddit.redditor("spez").unblock()

        """
        data = {
            "container": self._reddit.user.me().fullname,
            "name": str(self),
            "type": "enemy",
        }
        url = API_PATH["unfriend"].format(subreddit="all")
        self._reddit.post(url, data=data)

    def unfriend(self):
        """Unfriend the Redditor.

        For example, to unfriend Redditor ``spez``:

        .. code-block:: python

            reddit.redditor("spez").unfriend()

        """
        self._friend(method="DELETE", data={"id": str(self)})


class RedditorStream:
    """Provides submission and comment streams."""

    def __init__(self, redditor: "praw.models.Redditor"):
        """Create a RedditorStream instance.

        :param redditor: The redditor associated with the streams.

        """
        self.redditor = redditor

    def comments(
        self, **stream_options: Union[str, int, Dict[str, str]]
    ) -> Generator["praw.models.Comment", None, None]:
        """Yield new comments as they become available.

        Comments are yielded oldest first. Up to 100 historical comments will initially
        be returned.

        Keyword arguments are passed to :func:`.stream_generator`.

        For example, to retrieve all new comments made by redditor ``spez``, try:

        .. code-block:: python

            for comment in reddit.redditor("spez").stream.comments():
                print(comment)

        """
        return stream_generator(self.redditor.comments.new, **stream_options)

    def submissions(
        self, **stream_options: Union[str, int, Dict[str, str]]
    ) -> Generator["praw.models.Submission", None, None]:
        """Yield new submissions as they become available.

        Submissions are yielded oldest first. Up to 100 historical submissions will
        initially be returned.

        Keyword arguments are passed to :func:`.stream_generator`.

        For example, to retrieve all new submissions made by redditor ``spez``, try:

        .. code-block:: python

            for submission in reddit.redditor("spez").stream.submissions():
                print(submission)

        """
        return stream_generator(self.redditor.submissions.new, **stream_options)
