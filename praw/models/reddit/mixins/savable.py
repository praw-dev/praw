"""Provide the SavableMixin class."""
from typing import Optional

from ....const import API_PATH


class SavableMixin:
    """Interface for RedditBase classes that can be saved."""

    def save(self, category: Optional[str] = None):
        """Save the object.

        :param category: (Premium) The category to save to. If your user does not have
            Reddit Premium this value is ignored by Reddit (default: ``None``).

        Example usage:

        .. code-block:: python

            submission = reddit.submission(id="5or86n")
            submission.save(category="view later")

            comment = reddit.comment(id="dxolpyc")
            comment.save()

        .. seealso::

            :meth:`~.unsave`

        """
        self._reddit.post(
            API_PATH["save"], data={"category": category, "id": self.fullname}
        )

    def unsave(self):
        """Unsave the object.

        Example usage:

        .. code-block:: python

            submission = reddit.submission(id="5or86n")
            submission.unsave()

        comment = reddit.comment(id="dxolpyc") comment.unsave()

        .. seealso::

            :meth:`~.save`

        """
        self._reddit.post(API_PATH["unsave"], data={"id": self.fullname})
