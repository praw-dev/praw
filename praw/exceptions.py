"""PRAW exception classes.

Includes two main exceptions: :class:`.APIException` for when something goes
wrong on the server side, and :class:`.ClientException` when something goes
wrong on the client side. Both of these classes extend :class:`.PRAWException`.

"""
from typing import Optional


class PRAWException(Exception):
    """The base PRAW Exception that all other exception classes extend."""


class APIException(PRAWException):
    """Indicate exception that involve responses from Reddit's API."""

    def __init__(self, error_type: str, message: str, field: Optional[str]):
        """Initialize an instance of APIException.

        :param error_type: The error type set on Reddit's end.
        :param message: The associated message for the error.
        :param field: The input field associated with the error if available.

        .. note:: Calling ``str()`` on the instance returns
            ``unicode_escape``-d ASCII string because the message may be
            localized and may contain UNICODE characters. If you want a
            non-escaped message, access the ``message`` attribute on
            the instance.

        """
        error_str = u"{}: '{}'".format(error_type, message)
        if field:
            error_str += u" on field '{}'".format(field)
        error_str = error_str.encode("unicode_escape").decode("ascii")

        super().__init__(error_str)
        self.error_type = error_type
        self.message = message
        self.field = field


class ClientException(PRAWException):
    """Indicate exceptions that don't involve interaction with Reddit's API."""


class WebSocketException(ClientException):
    """Indicate exceptions caused by use of WebSockets."""

    def __init__(self, message, exception):
        """Initialize a WebSocketException.

        :param message: The exception message.
        :param exception: The exception thrown by the websocket library.
        """
        super().__init__(message)
        self.original_exception = exception
