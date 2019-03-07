"""Provide the GildableMixin class."""
from ....const import API_PATH


class GildableMixin(object):
    """Interface for classes that can be gilded."""

    def gild(self):
        """Gild the author of the item.

        .. note:: Requires the authenticated user to own reddit gold creddits.
                  Calling this method will consume one reddit gold creddit.

        Example usage:

        .. code:: python

           comment = reddit.comment('dkk4qjd')
           comment.gild()

           submission = reddit.submission('8dmv8z')
           submission.gild()

        """
        self._reddit.post(
            API_PATH["gild_thing"].format(fullname=self.fullname)
        )
