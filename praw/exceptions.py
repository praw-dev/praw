"""PRAW exception classes.

Includes two main exceptions: :class:`.APIException` for when something goes
wrong on the server side, and :class:`.ClientException` when something goes
wrong on the client side. Both of these classes extend :class:`.PRAWException`.

"""


class PRAWException(Exception):
    """The base PRAW Exception that all other exception classes extend."""


class APIException(PRAWException):
    """Indicate exception that involve responses from Reddit's API."""

    def __init__(self, error_type, message, field):
        """Initialize an instance of APIException.

        :param error_type: The error type set on Reddit's end.
        :param message: The associated message for the error.
        :param field: The input field associated with the error if available.

        """
        error_str = '{}: \'{}\''.format(error_type, message)
        if field:
            error_str += ' on field \'{}\''.format(field)
        super(APIException, self).__init__(error_str)
        self.error_type = error_type
        self.message = message
        self.field = field


class ClientException(PRAWException):
    """Indicate exceptions that don't involve interaction with Reddit's API."""
