"""Provide the Announcement class."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from praw.const import API_PATH
from praw.models.reddit.base import RedditBase
from praw.models.reddit.mixins.fullname import FullnameMixin

if TYPE_CHECKING:
    import praw


class Announcement(FullnameMixin, RedditBase):
    """A class that represents a Reddit announcement.

    .. include:: ../../typical_attributes.rst

    ================= =================================================================
    Attribute         Description
    ================= =================================================================
    ``body_html``     The announcement's body, rendered as HTML.
    ``body``          The announcement's body, in Markdown.
    ``id``            The fullname of the announcement, e.g. ``'ann_4sc833'``.
    ``permalink``     The announcement's permalink (to view on the web).
    ``read_at``       Timestamp the announcement was read, in ISO-8601 format. ``None``
                      if the announcement has not been read.
    ``read_datetime`` ``read_at`` as a timezone-aware :class:`datetime.datetime`, or
                      ``None`` if the announcement has not been read.
    ``sent_at``       Timestamp the announcement was sent, in ISO-8601 format.
    ``sent_datetime`` ``sent_at`` as a timezone-aware :class:`datetime.datetime`.
    ``subject``       The subject line of the announcement.
    ================= =================================================================

    """

    STR_FIELD = "id"

    @staticmethod
    def _parse_iso8601(value: str) -> datetime:
        # ``datetime.fromisoformat`` only accepts the ``Z`` suffix on Python 3.11+.
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()

    @property
    def _kind(self) -> str:
        """Return the object's kind shortcode."""
        return "ann"

    @property
    def read_datetime(self) -> datetime | None:
        """Return the time the announcement was read as a timezone-aware :class:`datetime.datetime`.

        Returns ``None`` if the announcement has not been read. The returned object is
        localized to the system's timezone.

        """
        if self.read_at is None:
            return None
        return self._parse_iso8601(self.read_at)

    @property
    def sent_datetime(self) -> datetime:
        """Return the time the announcement was sent as a timezone-aware :class:`datetime.datetime`.

        The returned object is localized to the system's timezone.

        """
        return self._parse_iso8601(self.sent_at)

    def __init__(
        self,
        reddit: praw.Reddit,
        id: str | None = None,
        _data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an :class:`.Announcement` instance."""
        if (id, _data).count(None) != 1:
            msg = "Exactly one of 'id' or '_data' must be provided."
            raise TypeError(msg)
        if id:
            self.id = id
        super().__init__(reddit, _data=_data, _fetched=_data is not None)

    def hide(self) -> None:
        """Hide the announcement.

        Example usage:

        .. code-block:: python

            for announcement in reddit.announcements():
                announcement.hide()

        .. seealso::

            :meth:`.AnnouncementHelper.hide` to hide multiple announcements at once.

        """
        self._reddit.post(API_PATH["hide_announcements"], data={"ids": self.fullname})

    def mark_read(self) -> None:
        """Mark the announcement as read.

        Example usage:

        .. code-block:: python

            for announcement in reddit.announcements():
                if announcement.read_at is None:
                    announcement.mark_read()

        .. seealso::

            - :meth:`.AnnouncementHelper.mark_read` to mark multiple announcements as
              read at once.
            - :meth:`.AnnouncementHelper.mark_all_read` to mark all announcements as
              read.

        """
        self._reddit.post(API_PATH["read_announcements"], data={"ids": self.fullname})
