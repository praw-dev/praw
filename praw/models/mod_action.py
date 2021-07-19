"""Provide the ModAction class."""
from typing import TYPE_CHECKING, Union

from .base import PRAWBase

if TYPE_CHECKING:  # pragma: no cover
    import praw


class ModAction(PRAWBase):
    """Represent a moderator action."""

    @property
    def mod(self) -> "praw.models.Redditor":
        """Return the :class:`.Redditor` who the action was issued by."""
        return self._reddit.redditor(self._mod)  # pylint: disable=no-member

    @mod.setter
    def mod(self, value: Union[str, "praw.models.Redditor"]):
        self._mod = value  # pylint: disable=attribute-defined-outside-init
