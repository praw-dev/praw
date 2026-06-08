"""Provide the CreatedMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class CreatedMixin:
    """Interface for objects that have a creation timestamp."""

    #: The attribute holding the creation `Unix Time`_, in seconds. Subclasses whose
    #: creation timestamp is stored under a different name override this.
    _created_at_attribute = "created_utc"

    @property
    def created_datetime(self) -> datetime:
        """Return the creation time as a timezone-aware :class:`datetime.datetime`.

        The returned object is localized to the system's timezone.

        """
        return self._to_local_datetime(getattr(self, self._created_at_attribute))
