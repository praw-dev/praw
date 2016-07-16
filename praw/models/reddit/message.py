"""Provide the Message class."""
from .base import RedditBase
from ...const import API_PATH
from .mixins import InboxableMixin


class Message(RedditBase, InboxableMixin):
    """A class for private messages."""

    @classmethod
    def parse(cls, data, reddit):
        """Return an instance of Message or SubredditMessage from ``data``.

        :param data: The structured data.
        :param reddit: An instance of :class:`.Reddit`.

        """
        if data.get('subreddit'):
            return SubredditMessage(reddit, _data=data)
        return cls(reddit, _data=data)

    def __init__(self, reddit, _data):
        """Construct an instance of the Message object."""
        super(Message, self).__init__(reddit, _data)


class SubredditMessage(Message):
    """A class for messages to a subreddit."""

    def mute(self, _unmute=False):
        """Mute the sender of this SubredditMessage."""
        self._reddit.post(API_PATH['mute_sender'], data={'id': self.fullname})

    def unmute(self):
        """Unmute the sender of this SubredditMessage."""
        self._reddit.post(API_PATH['unmute_sender'],
                          data={'id': self.fullname})
