"""Provide the Message class."""

from .mixins import InboxableMixin


class Message(InboxableMixin):
    """A class for private messages."""

    @staticmethod
    def from_id(reddit_session, message_id, *args, **kwargs):
        """Request the url for a Message and return a Message object.

        :param reddit_session: The session to make the request with.
        :param message_id: The ID of the message to request.

        The additional parameters are passed directly into
        :meth:`.request_json`.

        """
        # Reduce fullname to ID if necessary
        message_id = message_id.split('_', 1)[-1]
        url = reddit_session.config['message'].format(messageid=message_id)
        message_info = reddit_session.request_json(url, *args, **kwargs)
        message = message_info['data']['children'][0]

        # Messages are received as a listing such that
        # the first item is always the thread's root.
        # The ID requested by the user may be a child.
        if message.id == message_id:
            return message
        for child in message.replies:
            if child.id == message_id:
                return child

    def __init__(self, reddit_session, json_dict):
        """Construct an instance of the Message object."""
        super(Message, self).__init__(reddit_session, json_dict)
        if self.replies:
            self.replies = self.replies['data']['children']
        else:
            self.replies = []

    def __unicode__(self):
        """Return a string representation of the Message."""
        return 'From: {0}\nSubject: {1}\n\n{2}'.format(self.author,
                                                       self.subject, self.body)

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
