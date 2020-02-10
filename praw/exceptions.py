"""PRAW exception classes.

Includes two main exceptions: :class:`.APIException` for when something goes
wrong on the server side, and :class:`.ClientException` when something goes
wrong on the client side. Both of these classes extend :class:`.PRAWException`.

All other exceptions are subclassed from :class:`.ClientException`.

"""
from typing import List, Optional


class PRAWException(Exception):
    """The base PRAW Exception that all other exception classes extend."""


class APIException(PRAWException):
    """Indicate exception that involve responses from Reddit's API."""

    def __init__(self, error_type: str, message: str, field: Optional[str]):
        """Initialize an instance of APIException.

        :param error_type: The error type set on Reddit's end.
        :param message: The associated message for the error.
        :param field: The input field associated with the error if available.
        """
        error_str = "{}: '{}'".format(error_type, message)
        if field:
            error_str += " on field '{}'".format(field)

        super().__init__(error_str)
        self.error_type = error_type
        self.message = message
        self.field = field

class MultiAPIException(APIException):
    """A wrapper API exception that can deal with multiple API exceptions"""
    def __new__(cls, exceptions: List[List[str]]):
        """Returns APIException if len(exceptions) == 1 else instantizes.

        :param exceptions: A list containing the exception(s)
        :returns: :class:`.APIException` or :class:`.MultiAPIException`
        """
        if len(exceptions) == 1:
            return APIException(*exceptions[0])
        else:
            return super().__new__(cls)

    def __init__(self, exceptions: List[List[str]]):
        """Instantizes the class

        :param exceptions: A list containing the exceptions
        """
        self.api_exceptions = []
        arg_str = ""
        for exception in exceptions:
            self.api_exceptions.append(APIException(*exception))
            arg_str += self.api_exceptions[-1].args[0] + "\n"
        arg_str = arg_str.rstrip()
        Exception.__init__(self, arg_str)


class ClientException(PRAWException):
    """Indicate exceptions that don't involve interaction with Reddit's API."""


class DuplicateReplaceException(ClientException):
    """Indicate exceptions that involve the replacement of MoreComments."""

    def __init__(self):
        """Initialize the class."""
        super().__init__(
            "A duplicate comment has been detected. Are you attempting to call"
            " ``replace_more_comments`` more than once?"
        )


class InvalidImplicitAuth(ClientException):
    """Indicate exceptions where an implicit auth type is used incorrectly."""

    def __init__(self):
        """Instantize the class."""
        super().__init__(
            "Implicit authorization can only be used with installed apps."
        )


class InvalidURL(ClientException):
    """Indicate exceptions where an invalid URL is entered."""

    def __init__(self, url: str, message: str = "Invalid URL: {}"):
        """Initialize the class.

        :param url: The invalid URL.
        :param message: The message to display. Must contain a format
            identifier (``{}`` or ``{0}``). (default: ``"Invalid URL: {}"``)
        """
        super().__init__(message.format(url))


class MissingRequiredAttributeException(ClientException):
    """Indicate exceptions caused by not including a required attribute."""


class WebSocketException(ClientException):
    """Indicate exceptions caused by use of WebSockets."""

    def __init__(self, message: str, exception: Exception):
        """Initialize a WebSocketException.

        :param message: The exception message.
        :param exception: The exception thrown by the websocket library.
        """
        super().__init__(message)
        self.original_exception = exception
