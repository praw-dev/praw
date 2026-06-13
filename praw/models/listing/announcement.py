"""Provide the AnnouncementListing class."""

from __future__ import annotations

from praw.models.listing.listing import Listing


class AnnouncementListing(Listing):
    """Special :class:`.Listing` for handling :class:`.Announcement` lists.

    The announcements endpoint wraps results in ``{"after", "before", "data"}`` instead
    of the standard ``Listing`` envelope, with each child as a raw dict rather than a
    ``{"kind": "ann", "data": {...}}`` wrapper.

    """

    CHILD_ATTRIBUTE = "data"
