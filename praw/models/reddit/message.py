"""Provide the Message class."""
from ...const import API_PATH
from .base import RedditBase
from .mixins import InboxableMixin, ReplyableMixin
from .redditor import Redditor
from .subreddit import Subreddit


class Message(RedditBase, InboxableMixin, ReplyableMixin):
    """A class for private messages."""

    STR_FIELD = 'id'

    @classmethod
    def parse(cls, data, reddit):
        """Return an instance of Message or SubredditMessage from ``data``.

        :param data: The structured data.
        :param reddit: An instance of :class:`.Reddit`.

        """
        if data['author']:
            data['author'] = Redditor(reddit, data['author'])

        if data['dest'].startswith('#'):
            data['dest'] = Subreddit(reddit, data['dest'][1:])
        else:
            data['dest'] = Redditor(reddit, data['dest'])

        if data['replies']:
            replies = data['replies']
            data['replies'] = reddit._objector.objectify(
                replies['data']['children'])
        else:
            data['replies'] = []

        if data['subreddit']:
            data['subreddit'] = Subreddit(reddit, data['subreddit'])
            return SubredditMessage(reddit, _data=data)

        return cls(reddit, _data=data)

    def __init__(self, reddit, _data):
        """Construct an instance of the Message object."""
        super(Message, self).__init__(reddit, _data)
        self._fetched = True

    def delete(self):
        """Delete the message.

        .. note:: Reddit does not return an indication of whether or not the
                  message was successfully deleted.
        """
        self._reddit.post(API_PATH['delete_message'],
                          data={'id': self.fullname})


class SubredditMessage(Message):
    """A class for messages to a subreddit."""

    def mute(self, _unmute=False):
        """Mute the sender of this SubredditMessage."""
        self._reddit.post(API_PATH['mute_sender'], data={'id': self.fullname})

    def unmute(self):
        """Unmute the sender of this SubredditMessage."""
        self._reddit.post(API_PATH['unmute_sender'],
                          data={'id': self.fullname})
