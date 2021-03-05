"""Provide the ModeratedList class."""
from .base import BaseList


class ModeratedList(BaseList):
    """A list of Moderated Subreddits. Works just like a regular list."""

    CHILD_ATTRIBUTE = "data"
