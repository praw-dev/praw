"""PRAW exception classes.

Includes two main exceptions: :class:`.APIException` for when something goes
wrong on the server side, and :class:`.ClientException` when something goes
wrong on the client side. Both of these classes extend :class:`.PRAWException`.

All other exceptions are subclassed from :class:`.ClientException`.

"""
from typing import Iterator, List, Optional, Union


class PRAWException(Exception):
    """The base PRAW Exception that all other exception classes extend."""


class APIException(PRAWException):
    """Indicate exception that involve responses from Reddit's API."""

    @staticmethod
    def _exception_str(
        error_type: str,
        message: str,
        field: Optional[str],
        newline: bool = False,
    ):
        error_str = "{}: '{}'".format(error_type, message)
        error_str += " on field '{}'".format(field) if field else ""
        error_str += "\n" if newline else ""
        return error_str

    def __init__(
        self,
        error_type: Union[str, List[List[str]]],
        message: Optional[str] = None,
        field: Optional[str] = None,
    ):
        """Initialize an instance of APIException.

        :param error_type: The error type set on Reddit's end.
        :param message: The associated message for the error.
        :param field: The input field associated with the error if available.
        """
        error_str = ""
        if isinstance(error_type, list):
            errors = error_type
            if len(errors) == 1:
                error_type, message, field = errors[0]
                error_str += self._exception_str(error_type, message, field)
            else:
                error_type, message, field = [], [], []
                for error in errors:
                    cur_error, cur_message, cur_field = error
                    error_type.append(cur_error)
                    message.append(cur_message)
                    field.append(cur_field)
                    error_str += self._exception_str(
                        cur_error, cur_message, cur_field, newline=True
                    )
        else:
            error_str += self._exception_str(error_type, message, field)
        error_str = error_str.rstrip()
        super().__init__(error_str)
        self.error_type = error_type
        self.message = message
        self.field = field

    def __iter__(self) -> Iterator[str]:
        """Iterate over the sub-exceptions."""
        return iter(self.args[0].split("\n"))


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
