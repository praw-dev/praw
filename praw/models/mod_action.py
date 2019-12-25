"""Provide the ModAction class."""

from .base import PRAWBase


class ModAction(PRAWBase):
    """Represent a moderator action."""

    @property
    def mod(self):
        """Return the Redditor who the action was issued by."""
        return self._reddit.redditor(self._mod)  # pylint: disable=no-member

    @mod.setter
    def mod(self, value):
        self._mod = value  # pylint: disable=attribute-defined-outside-init
