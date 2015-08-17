    def __init__(self, message=None, url):
        """Construct a OAuthException.

        :param message: The message associated with the exception.
        :param url: The url that resulted in error.

        """
        if not message:
            message = 'Error'
        message = message + " on url {0}".format(url)
        super(OAuthException, self).__init__(message)
