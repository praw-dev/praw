"""Provide the RedditorList class."""
from ..reddit.redditor import Redditor
from .base import BaseList


class RedditorList(BaseList):
    """A list of Redditors. Works just like a regular list."""

    CHILD_ATTRIBUTE = 'children'

    @staticmethod
    def _convert(reddit, data):
        """Return a Redditor object from the data."""
        return Redditor(reddit, data['name'])
