"""Provide the TrophyList class."""
from .base import BaseList


class TrophyList(BaseList):
    """A list of trophies.

    This class is solely used to parse responses from reddit, so end users should not
    use this class directly.

    """

    CHILD_ATTRIBUTE = "trophies"
