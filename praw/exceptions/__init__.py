"""PRAW exception classes.

Includes two main exceptions: :class:`.RedditAPIException` for when something
goes wrong on the server side, and :class:`.ClientException` when something
goes wrong on the client side. Both of these classes extend
:class:`.PRAWException`.

All other exceptions are subclassed from :class:`.ClientException`.
"""
# flake8: noqa
from .api import (
    APIException,
    RedditAPIException,
    RedditErrorItem,
)
from .base import PRAWException
from .client import (
    ClientException,
    DuplicateReplaceException,
    InvalidFlairTemplateID,
    InvalidImplicitAuth,
    InvalidURL,
    MissingRequiredAttributeException,
    TooLargeMediaException,
    WebSocketException,
)
