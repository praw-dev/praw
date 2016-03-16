"""PRAW exception classes.

Includes two main exceptions: ``APIExeception`` for when something goes wrong
on the server side, and ``ClientException`` when something goes wrong on the
client side. Both of these classes extend ``PRAWException``.

"""


class PRAWException(Exception):
    """The base PRAW Exception that all other exception classes extend."""


class APIException(PRAWException):
    """Indicate exception that involve responses from reddit's API."""

    def __init__(self, error_type, message, field, http_response=None):
        """Construct an APIException.

        :param error_type: The error type set on reddit's end.
        :param message: The associated message for the error.
        :param field: The input field associated with the error, or ''.
        :param http_response: The HTTP response that resulted in the exception.

        """
        super(APIException, self).__init__('{}: {!r} on field {!r}'
                                           .format(error_type, message, field))
        self.error_type = error_type
        self.message = message
        self.field = field
        self.http_response = http_response


class ClientException(PRAWException):
    """Indicate exceptions that don't involve interaction with reddit's API."""
