"""Provide the ModAction class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from praw.models.base import PRAWBase

if TYPE_CHECKING:
    from praw import models


class ModAction(PRAWBase):
    """Represent a moderator action."""

    @property
    def mod(self) -> models.Redditor:
        """Return the :class:`.Redditor` who the action was issued by."""
        return self._reddit.redditor(self._mod)

    @mod.setter
    def mod(self, value: str | models.Redditor) -> None:
        self._mod = value
