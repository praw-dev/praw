"""Provide the ModeratedList class."""

from praw.models.list.base import BaseList


class ModeratedList(BaseList):
    """A list of moderated :class:`.Subreddit` objects. Works just like a regular list."""

    CHILD_ATTRIBUTE = "data"
