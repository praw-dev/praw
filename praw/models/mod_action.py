"""Provide the ModAction class."""
from typing import TYPE_CHECKING

from .base import PRAWBase

if TYPE_CHECKING:  # pragma: no cover
    from .reddit.redditor import Redditor


class ModAction(PRAWBase):
    """Represent a moderator action."""

    @property
    def mod(self) -> "Redditor":
        """Return the Redditor who the action was issued by."""
        return self._reddit.redditor(self._mod)  # pylint: disable=no-member

    @mod.setter
    def mod(self, value: "Redditor"):
        self._mod = value  # pylint: disable=attribute-defined-outside-init
