"""Provide the MessageableMixin class."""
from ....const import API_PATH


class MessageableMixin(object):
    """Interface for classes that can be messaged."""

    def message(self, subject, message, from_subreddit=None):
        """
        Send a message to a redditor or a subreddit's moderators (mod mail).

        :param subject: The subject of the message.
        :param message: The message content.
        :param from_subreddit: A Subreddit instance or string to send the
            message from. When provided, messages are sent from the subreddit
            rather than from the authenticated user. Note that the
            authenticated user must be a moderator of the subreddit and have
            mail permissions.

        For example, to send a private message to ``/u/spez``, try:

        .. code:: python

           reddit.redditor('spez').message('TEST', 'test message from PRAW')

        To send a message to ``u/spez`` from the moderators of ``r/test`` try:

        .. code:: python

           reddit.redditor('spez').message('TEST', 'test message from r/test',
                                           from_subreddit='test')

        To send a message to the moderators of ``/r/test``, try:

        .. code:: python

           reddit.subreddit('test').message('TEST', 'test PM from PRAW')

        """
        data = {
            "subject": subject,
            "text": message,
            "to": "{}{}".format(
                getattr(self.__class__, "MESSAGE_PREFIX", ""), self
            ),
        }
        if from_subreddit:
            data["from_sr"] = str(from_subreddit)
        self._reddit.post(API_PATH["compose"], data=data)
