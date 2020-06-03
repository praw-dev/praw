"""Provide the GildableMixin class."""
from ....const import API_PATH


class GildableMixin:
    """Interface for classes that can be gilded."""

    def gild(self):
        """Gild the author of the item.

        .. note:: Requires the authenticated user to own Reddit Coins.
                  Calling this method will consume Reddit Coins.

        Example usage:

        .. code-block:: python

           comment = reddit.comment("dkk4qjd")
           comment.gild()

           submission = reddit.submission("8dmv8z")
           submission.gild()

        """
        self._reddit.post(API_PATH["gild_thing"].format(fullname=self.fullname))
