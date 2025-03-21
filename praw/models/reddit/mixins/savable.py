"""Provide the SavableMixin class."""

from __future__ import annotations

from praw.const import API_PATH


class SavableMixin:
    """Interface for :class:`.RedditBase` classes that can be saved."""

    def save(self, *, category: str | None = None) -> None:
        """Save the object.

        :param category: The category to save to. If the authenticated user does not
            have Reddit Premium this value is ignored by Reddit (default: ``None``).

        Example usage:

        .. code-block:: python

            submission = reddit.submission("5or86n")
            submission.save(category="view later")

            comment = reddit.comment("dxolpyc")
            comment.save()

        .. seealso::

            :meth:`.unsave`

        """
        self._reddit.post(API_PATH["save"], data={"category": category, "id": self.fullname})

    def unsave(self) -> None:
        """Unsave the object.

        Example usage:

        .. code-block:: python

            submission = reddit.submission("5or86n")
            submission.unsave()

            comment = reddit.comment("dxolpyc")
            comment.unsave()

        .. seealso::

            :meth:`.save`

        """
        self._reddit.post(API_PATH["unsave"], data={"id": self.fullname})
