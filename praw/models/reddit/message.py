"""Provide the Message class."""

from .base import RedditBase
from .mixins import InboxableMixin


class Message(RedditBase, InboxableMixin):
    """A class for private messages."""

    def __init__(self, reddit, _data):
        """Construct an instance of the Message object."""
        super(Message, self).__init__(reddit, _data)

    def collapse(self):
        """Collapse a private message or modmail."""
        url = self.reddit_session.config['collapse_message']
        self.reddit_session.request_json(url, data={'id': self.name})

    def mute_modmail_author(self, _unmute=False):
        """Mute the sender of this modmail message.

        :param _unmute: Unmute the user instead. Please use
            :meth:`unmute_modmail_author` instead of setting this directly.

        """
        path = 'unmute_sender' if _unmute else 'mute_sender'
        return self.reddit_session.request_json(
            self.reddit_session.config[path], data={'id': self.fullname})

    def uncollapse(self):
        """Uncollapse a private message or modmail."""
        url = self.reddit_session.config['uncollapse_message']
        self.reddit_session.request_json(url, data={'id': self.name})

    def unmute_modmail_author(self):
        """Unmute the sender of this modmail message."""
        return self.mute_modmail_author(_unmute=True)
