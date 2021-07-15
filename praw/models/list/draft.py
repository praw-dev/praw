"""Provide the DraftList class."""

from .base import BaseList


class DraftList(BaseList):
    r"""A list of :class:`.Draft`\ s. Works just like a regular list."""

    CHILD_ATTRIBUTE = "drafts"
