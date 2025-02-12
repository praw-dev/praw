"""Provide the RedditorList class."""

from praw.models.list.base import BaseList


class RedditorList(BaseList):
    """A list of :class:`.Redditor` objects. Works just like a regular list."""

    CHILD_ATTRIBUTE = "children"
