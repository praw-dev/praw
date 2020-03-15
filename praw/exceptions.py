"""PRAW exception classes.

Includes two main exceptions: :class:`.RedditAPIException` for when something
goes wrong on the server side, and :class:`.ClientException` when something
goes wrong on the client side. Both of these classes extend
:class:`.PRAWException`.

All other exceptions are subclassed from :class:`.ClientException`.

"""
from typing import List, Optional, TypeVar, Union
from warnings import warn

_RedditErrorItem = TypeVar("_RedditErrorItem")


class PRAWException(Exception):
    """The base PRAW Exception that all other exception classes extend."""


class RedditErrorItem:
    """Represents a single error returned from Reddit's API."""

    @property
    def error_message(self):
        """Get the completed error message string."""
        error_str = "{}: {!r}".format(self.error_type, self.message)
        if self.field:
            error_str += " on field {!r}".format(self.field)
        return error_str

    def __init__(
        self, error_type: str, message: str, field: Optional[str] = None
    ):
        """Instantiate an error item.

        :param error_type: The error type set on Reddit's end.
        :param message: The associated message for the error.
        :param field: The input field associated with the error, if available.
        """
        self.error_type = error_type
        self.message = message
        self.field = field

    def __eq__(self, other: Union[_RedditErrorItem, List[str]]):
        """Check for equality."""
        if isinstance(other, RedditErrorItem):
            return (self.error_type, self.message, self.field) == (
                other.error_type,
                other.message,
                other.field,
            )
        return super().__eq__(other)

    def __repr__(self):
        """Return repr(self)."""
        return "{}(error_type={!r}, message={!r}, field={!r})".format(
            self.__class__.__name__, self.error_type, self.message, self.field
        )

    def __str__(self):
        """Get the message returned from str(self)."""
        return self.error_message


class APIException(PRAWException):
    """Old class preserved for alias purposes."""

    @staticmethod
    def parse_exception_list(
        exceptions: List[Union[RedditErrorItem, List[str]]]
    ):
        """Covert an exception list into a :class:`.RedditErrorItem` list."""
        return [
            exception
            if isinstance(exception, RedditErrorItem)
            else RedditErrorItem(
                exception[0],
                exception[1],
                exception[2] if bool(exception[2]) else "",
            )
            for exception in exceptions
        ]

    @property
    def error_type(self) -> str:
        """Get error_type."""
        return self._get_old_attr("error_type")

    @property
    def message(self) -> str:
        """Get message."""
        return self._get_old_attr("message")

    @property
    def field(self) -> str:
        """Get field."""
        return self._get_old_attr("field")

    def _get_old_attr(self, attrname):
        warn(
            "Accessing attribute ``{}`` through APIException is deprecated. "
            "This behavior will be removed in PRAW 8.0. Check out "
            "https://praw.readthedocs.io/en/latest/package_info/"
            "praw7_migration.html to learn how to migrate your code.".format(
                attrname
            ),
            category=DeprecationWarning,
            stacklevel=3,
        )
        return getattr(self.items[0], attrname)

    def __init__(
        self,
        items: Union[List[Union[RedditErrorItem, List[str], str]], str],
        *optional_args: str
    ):
        """Initialize an instance of RedditAPIException.

        :param items: Either a list of instances of :class:`.RedditErrorItem`
            or a list containing lists of unformed errors.
        :param optional_args: Takes the second and third arguments that
            :class:`.APIException` used to take.
        """
        if isinstance(items, str):
            items = [[items, *optional_args]]
        elif isinstance(items, list) and isinstance(items[0], str):
            items = [items]
        self.items = self.parse_exception_list(items)
        super().__init__(*self.items)


class RedditAPIException(APIException):
    """Container for error messages from Reddit's API."""


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
