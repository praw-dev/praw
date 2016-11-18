"""Provide the ModAction class."""

from ..base import PRAWBase
from .redditor import Redditor


class ModAction(PRAWBase):
    """Represent a moderator action."""

    @property
    def mod(self):
        """Return the Redditor who the action was issued by."""
        return Redditor(self._reddit, name=self._mod)

    @mod.setter
    def mod(self, value):
        self._mod = value
