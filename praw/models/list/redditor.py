"""Provide the RedditorList class."""
from .base import BaseList


class RedditorList(BaseList):
    r"""A list of :class:`.Redditor`\ s. Works just like a regular list."""

    CHILD_ATTRIBUTE = "children"
