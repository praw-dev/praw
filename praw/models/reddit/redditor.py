"""Provide the Redditor class."""
from json import dumps
from typing import Any, Dict, Generator, List, Optional, TypeVar, Union

from ...const import API_PATH
from ...util.cache import cachedproperty
from ..listing.mixins import RedditorListingMixin
from ..util import stream_generator
from .base import RedditBase
from .mixins import FullnameMixin, MessageableMixin

_Redditor = TypeVar("_Redditor")
_RedditorStream = TypeVar("_RedditorStream")
Comment = TypeVar("Comment")
Multireddit = TypeVar("Multireddit")
Reddit = TypeVar("Reddit")
Submission = TypeVar("Submission")
Subreddit = TypeVar("Subreddit")
Trophy = TypeVar("Trophy")


class Redditor(
    MessageableMixin, RedditorListingMixin, FullnameMixin, RedditBase
):
    """A class representing the users of reddit.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ==================================== ======================================
    Attribute                            Description
    ==================================== ======================================
    ``comment_karma``                    The comment karma for the Redditor.
    ``comments``                         Provide an instance of
                                         :class:`.SubListing` for comment
                                         access.
    ``created_utc``                      Time the account was created,
                                         represented in `Unix Time`_.
    ``has_verified_email``               Whether or not the Redditor has
                                         verified their email.
    ``icon_img``                         The url of the Redditors' avatar.
    ``id``                               The ID of the Redditor.
    ``is_employee``                      Whether or not the Redditor is a
                                         Reddit employee.
    ``is_friend``                        Whether or not the Redditor is friends
                                         with the authenticated user.
    ``is_mod``                           Whether or not the Redditor mods any
                                         subreddits.
    ``is_gold``                          Whether or not the Redditor has active
                                         Reddit Premium status.
    ``link_karma``                       The link karma for the Redditor.
    ``name``                             The Redditor's username.
    ``subreddit``                        If the Redditor has created a
                                         user-subreddit, provides a dictionary
                                         of additional attributes. See below.
    ``subreddit['banner_img']``          The URL of the user-subreddit banner.
    ``subreddit['name']``                The fullname of the user-subreddit.
    ``subreddit['over_18']``             Whether or not the user-subreddit is
                                         NSFW.
    ``subreddit['public_description']``  The public description of the user-
                                         subreddit.
    ``subreddit['subscribers']``         The number of users subscribed to the
                                         user-subreddit.
    ``subreddit['title']``               The title of the user-subreddit.
    ==================================== ======================================


    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time

    """

    STR_FIELD = "name"

    @classmethod
    def from_data(cls, reddit, data):
        """Return an instance of Redditor, or None from ``data``."""
        if data == "[deleted]":
            return None
        return cls(reddit, data)

    @cachedproperty
    def stream(self) -> _RedditorStream:
        """Provide an instance of :class:`.RedditorStream`.

        Streams can be used to indefinitely retrieve new comments made by a
        redditor, like:

        .. code:: python

           for comment in reddit.redditor('spez').stream.comments():
               print(comment)

        Additionally, new submissions can be retrieved via the stream. In the
        following example all submissions are fetched via the redditor
        ``spez``:

        .. code:: python

           for submission in reddit.redditor('spez').stream.submissions():
               print(submission)

        """
        return RedditorStream(self)

    @property
    def _kind(self):
        """Return the class's kind."""
        return self._reddit.config.kinds["redditor"]

    @property
    def _path(self):
        return API_PATH["user"].format(user=self)

    def __init__(
        self,
        reddit: Reddit,
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
        if [name, fullname, _data].count(None) != 2:
            raise TypeError(
                "Exactly one of `name`, `fullname`, or `_data` must be "
                "provided."
            )
        if _data:
            assert (
                isinstance(_data, dict) and "name" in _data
            ), "Please file a bug with PRAW"
        super().__init__(reddit, _data=_data)
        self._listing_use_sort = True
        if name:
            self.name = name
        elif fullname:
            self._fullname = fullname

    def _fetch_username(self, fullname):
        return self._reddit.get(
            API_PATH["user_by_fullname"], params={"ids": fullname}
        )[fullname]["name"]

    def _fetch_info(self):
        if hasattr(self, "_fullname"):
            self.name = self._fetch_username(self._fullname)
        return ("user_about", {"user": self.name}, None)

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
        """Block the Redditor."""
        self._reddit.post(
            API_PATH["block_user"], params={"account_id": self.fullname}
        )

    def friend(self, note: str = None):
        """Friend the Redditor.

        :param note: A note to save along with the relationship. Requires
            Reddit Premium (default: None).

        Calling this method subsequent times will update the note.

        """
        self._friend("PUT", data={"note": note} if note else {})

    def friend_info(self) -> _Redditor:
        """Return a Redditor instance with specific friend-related attributes.

        :returns: A :class:`.Redditor` instance with fields ``date``, ``id``,
            and possibly ``note`` if the authenticated user has Reddit Premium.

        """
        return self._reddit.get(API_PATH["friend_v1"].format(user=self))

    def gild(self, months: int = 1):
        """Gild the Redditor.

        :param months: Specifies the number of months to gild up to 36
            (default: 1).

        """
        if months < 1 or months > 36:
            raise TypeError("months must be between 1 and 36")
        self._reddit.post(
            API_PATH["gild_user"].format(username=self),
            data={"months": months},
        )

    def moderated(self) -> List[Subreddit]:
        """Return a list of the redditor's moderated subreddits.

        :returns: A ``list`` of :class:`~praw.models.Subreddit` objects.
            Return ``[]`` if the redditor has no moderated subreddits.

        .. note:: The redditor's own user profile subreddit will not be
           returned, but other user profile subreddits they moderate
           will be returned.

        Usage:

        .. code:: python

            for subreddit in reddit.redditor('spez').moderated():
                print(subreddit.display_name)
                print(subreddit.title)

        """
        modded_data = self._reddit.get(API_PATH["moderated"].format(user=self))
        if "data" not in modded_data:
            return []
        else:
            subreddits = [
                self._reddit.subreddit(x["sr"]) for x in modded_data["data"]
            ]
            return subreddits

    def multireddits(self) -> List[Multireddit]:
        """Return a list of the redditor's public multireddits."""
        return self._reddit.get(API_PATH["multireddit_user"].format(user=self))

    def trophies(self) -> List[Trophy]:
        """Return a list of the redditor's trophies.

        :returns: A ``list`` of :class:`~praw.models.Trophy` objects.
            Return ``[]`` if the redditor has no trophy.

        Raise ``prawcore.exceptions.BadRequest`` if the redditor doesn't exist.

        Usage:

        .. code:: python

            for trophy in reddit.redditor('spez').trophies():
                print(trophy.name)
                print(trophy.description)

        """
        return list(self._reddit.get(API_PATH["trophies"].format(user=self)))

    def unblock(self):
        """Unblock the Redditor."""
        data = {
            "container": self._reddit.user.me().fullname,
            "name": str(self),
            "type": "enemy",
        }
        url = API_PATH["unfriend"].format(subreddit="all")
        self._reddit.post(url, data=data)

    def unfriend(self):
        """Unfriend the Redditor."""
        self._friend(method="DELETE", data={"id": str(self)})


class RedditorStream:
    """Provides submission and comment streams."""

    def __init__(self, redditor: Redditor):
        """Create a RedditorStream instance.

        :param redditor: The redditor associated with the streams.

        """
        self.redditor = redditor

    def comments(
        self, **stream_options: Union[str, int, Dict[str, str]]
    ) -> Generator[Comment, None, None]:
        """Yield new comments as they become available.

        Comments are yielded oldest first. Up to 100 historical comments will
        initially be returned.

        Keyword arguments are passed to :func:`.stream_generator`.

        For example, to retrieve all new comments made by redditor ``spez``,
        try:

        .. code:: python

           for comment in reddit.redditor('spez').stream.comments():
               print(comment)

        """
        return stream_generator(self.redditor.comments.new, **stream_options)

    def submissions(
        self, **stream_options: Union[str, int, Dict[str, str]]
    ) -> Generator[Submission, None, None]:
        """Yield new submissions as they become available.

        Submissions are yielded oldest first. Up to 100 historical submissions
        will initially be returned.

        Keyword arguments are passed to :func:`.stream_generator`.

        For example to retrieve all new submissions made by redditor
        ``spez``, try:

        .. code:: python

           for submission in reddit.redditor('spez').stream.submissions():
               print(submission)

        """
        return stream_generator(
            self.redditor.submissions.new, **stream_options
        )
