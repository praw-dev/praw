"""Provide the RedditorList class."""
from .base import BaseList


class RedditorList(BaseList):
    """A list of Redditors. Works just like a regular list."""

    CHILD_ATTRIBUTE = "children"
