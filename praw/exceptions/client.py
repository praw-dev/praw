"""Container for client-side errors."""

from .base import PRAWException


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


class InvalidFlairTemplateID(ClientException):
    """Indicate exceptions where an invalid flair template id is given."""

    def __init__(self, template_id: str):
        """Initialize the class."""
        super().__init__(
            "The flair template id ``{template_id}`` is invalid. If you are "
            "trying to create a flair, please use the ``add`` method.".format(
                template_id=template_id
            )
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


class TooLargeMediaException(ClientException):
    """Indicate exceptions from uploading media that's too large."""

    def __init__(self, maximum_size: int, actual: int):
        """Initialize a TooLargeMediaException.

        :param maximum_size: The maximum_size size of the uploaded media.
        :param actual: The actual size of the uploaded media.
        """
        self.maximum_size = maximum_size
        self.actual = actual
        super().__init__(
            "The media that you uploaded was too large (maximum size is "
            "{maximum_size} bytes, uploaded {actual} bytes)".format(
                maximum_size=maximum_size, actual=actual
            )
        )


class WebSocketException(ClientException):
    """Indicate exceptions caused by use of WebSockets."""

    def __init__(self, message: str, exception: Exception):
        """Initialize a WebSocketException.

        :param message: The exception message.
        :param exception: The exception thrown by the websocket library.
        """
        super().__init__(message)
        self.original_exception = exception
