"""Provide the ModNote class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from praw.endpoints import API_PATH
from praw.models.base import DynamicAttributes, PRAWBase
from praw.models.reddit.mixins import CreatedMixin

if TYPE_CHECKING:
    import praw.models


class ModNote(DynamicAttributes, CreatedMixin, PRAWBase):
    """Represent a moderator note.

    .. include:: ../../typical_attributes.rst

    =============== ====================================================================
    Attribute       Description
    =============== ====================================================================
    ``action``      If this note represents a moderator action, this field indicates the
                    type of action. For example, ``"banuser"`` if the action was banning
                    a user.
    ``created_at``  Time the moderator note was created, represented in `Unix Time`_.
    ``description`` If this note represents a moderator action, this field indicates the
                    description of the action. For example, if the action was banning
                    the user, this is the ban reason.
    ``details``     If this note represents a moderator action, this field indicates the
                    details of the action. For example, if the action was banning the
                    user, this is the duration of the ban.
    ``id``          The ID of the moderator note.
    ``label``       The label applied to the note, currently one of:
                    ``"ABUSE_WARNING"``, ``"BAN"``, ``"BOT_BAN"``, ``"HELPFUL_USER"``,
                    ``"PERMA_BAN"``, ``"SOLID_CONTRIBUTOR"``, ``"SPAM_WARNING"``,
                    ``"SPAM_WATCH"``, or ``None``.
    ``moderator``   The moderator who created the note.
    ``note``        The text of the note.
    ``reddit_id``   The fullname of the object this note is attributed to, or ``None``
                    if not set. If this note represents a moderators action, this is the
                    fullname of the object the action was performed on.
    ``subreddit``   The subreddit this note belongs to.
    ``type``        The type of note, currently one of: ``"APPROVAL"``, ``"BAN"``,
                    ``"CONTENT_CHANGE"``, ``"INVITE"``, ``"MUTE"``, ``"NOTE"``,
                    ``"REMOVAL"``, or ``"SPAM"``.
    ``user``        The redditor the note is for.
    =============== ====================================================================

    .. _unix time: https://en.wikipedia.org/wiki/Unix_time

    """

    _created_at_attribute = "created_at"

    id: str
    subreddit: praw.models.Subreddit
    user: praw.models.Redditor

    def __eq__(self, other: ModNote | str | object) -> bool:
        """Return whether the other instance equals the current."""
        if isinstance(other, self.__class__):
            return self.id == other.id
        if isinstance(other, str):
            return self.id == other
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Return the hash of the current instance."""
        return hash(self.__class__.__name__) ^ hash(self.id)

    def delete(self) -> None:
        """Delete this note.

        For example, to delete the last note for u/spez from r/test, try:

        .. code-block:: python

            for note in reddit.subreddit("test").mod.notes("spez"):
                note.delete()

        """
        params: dict[str, str | int] = {
            "note_id": self.id,
            "subreddit": str(self.subreddit),
            "user": str(self.user),
        }
        self._reddit.delete(API_PATH["mod_notes"], params=params)
