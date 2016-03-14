"""Provide the MessageableMixin class."""


class MessageableMixin(object):
    """Interface for classes that can be messaged.

    def message(self, recipient, subject, message, from_sr=None, captcha=None,
                **kwargs):
        Send a message to a redditor or a subreddit's moderators (mod mail).

        :param recipient: A Redditor or Subreddit instance to send a message
            to. A string can also be used in which case the string is treated
            as a redditor unless it is prefixed with either '/r/' or '#', in
            which case it will be treated as a subreddit.
        :param subject: The subject of the message to send.
        :param message: The actual message content.
        :param from_sr: A Subreddit instance or string to send the message
            from. When provided, messages are sent from the subreddit rather
            than from the authenticated user. Note that the authenticated user
            must be a moderator of the subreddit and have mail permissions.

        :returns: The json response from the server.

        This function may result in a captcha challenge. PRAW will
        automatically prompt you for a response. See :ref:`handling-captchas`
        if you want to manually handle captchas.


        if isinstance(recipient, models.Subreddit):
            recipient = '/r/{0}'.format(six.text_type(recipient))
        else:
            recipient = six.text_type(recipient)

        data = {'text': message,
                'subject': subject,
                'to': recipient}
        if from_sr:
            data['from_sr'] = six.text_type(from_sr)
        if captcha:
            data.update(captcha)
        response = self.request_json(self.config['compose'], data=data,
                                     retry_on_error=False)
        return response
    """
