"""Provide the Message class."""
from ...const import API_PATH
from .base import RedditBase
from .mixins import FullnameMixin, InboxableMixin, ReplyableMixin
from .redditor import Redditor
from .subreddit import Subreddit


class Message(InboxableMixin, ReplyableMixin, FullnameMixin, RedditBase):
    """A class for private messages.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    comprehensive in any way.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``author``              Provides an instance of :class:`.Redditor`.
    ``body``                The body of the message.
    ``created_utc``         Time the message was created, represented in
                            `Unix Time`_.
    ``dest``                Provides an instance of :class:`.Redditor`. The
                            recipient of the message.
    ``id``                  The ID of the message.
    ``name``                The full ID of the message, prefixed with 't4'.
    ``subject``             The subject of the message.
    ``subreddit``           If the message was sent from a subreddit,
                            provides an instance of :class:`.Subreddit`.
    ``was_comment``         Whether or not the message was a comment reply.
    ======================= ===================================================


    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time

    """

    STR_FIELD = "id"

    @classmethod
    def parse(cls, data, reddit):
        """Return an instance of Message or SubredditMessage from ``data``.

        :param data: The structured data.
        :param reddit: An instance of :class:`.Reddit`.

        """
        if data["author"]:
            data["author"] = Redditor(reddit, data["author"])

        if data["dest"].startswith("#"):
            data["dest"] = Subreddit(reddit, data["dest"][1:])
        else:
            data["dest"] = Redditor(reddit, data["dest"])

        if data["replies"]:
            replies = data["replies"]
            data["replies"] = reddit._objector.objectify(
                replies["data"]["children"]
            )
        else:
            data["replies"] = []

        if data["subreddit"]:
            data["subreddit"] = Subreddit(reddit, data["subreddit"])
            return SubredditMessage(reddit, _data=data)

        return cls(reddit, _data=data)

    @property
    def _kind(self):
        """Return the class's kind."""
        return self._reddit.config.kinds["message"]

    def __init__(self, reddit, _data):
        """Construct an instance of the Message object."""
        super(Message, self).__init__(reddit, _data=_data)
        self._fetched = True

    def delete(self):
        """Delete the message.

        .. note:: Reddit does not return an indication of whether or not the
                  message was successfully deleted.
        """
        self._reddit.post(
            API_PATH["delete_message"], data={"id": self.fullname}
        )


class SubredditMessage(Message):
    """A class for messages to a subreddit."""

    def mute(self, _unmute=False):
        """Mute the sender of this SubredditMessage."""
        self._reddit.post(API_PATH["mute_sender"], data={"id": self.fullname})

    def unmute(self):
        """Unmute the sender of this SubredditMessage."""
        self._reddit.post(
            API_PATH["unmute_sender"], data={"id": self.fullname}
        )
