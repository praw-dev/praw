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
        :returns: The json response from the server.

        """
        data = {'subject': subject, 'text': message,
                'to': '{}{}'.format(getattr(
                    self.__class__, 'MESSAGE_PREFIX', ''), self)}
        if from_subreddit:
            data['from_sr'] = str(from_subreddit)
        return self._reddit.post(API_PATH['compose'], data=data)
