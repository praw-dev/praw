"""Provide the MessageableMixin class."""
from ..redditmodel import RedditModel


class MessageableMixin(RedditModel):
    """Interface for RedditModel classes that can be messaged."""

    _methods = (('send_message', 'PMMix'),)
