"""Provide the FullnameMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING


class FullnameMixin:
    """Interface for classes that have a fullname."""

    if TYPE_CHECKING:
        # Provided by the host class (:class:`.RedditBase`).
        id: str

    @property
    def _kind(self) -> str | None:
        """Return the object's kind shortcode (e.g. ``t1``); overridden by subclasses."""
        return None

    @property
    def fullname(self) -> str:
        """Return the object's fullname.

        A fullname is an object's kind mapping like ``t3`` followed by an underscore and
        the object's base36 ID, e.g., ``t1_c5s96e0``.

        """
        if "_" in self.id:
            return self.id
        return f"{self._kind}_{self.id}"
