"""Provide the SavableMixin class."""
from ....const import API_PATH


class SavableMixin(object):
    """Interface for RedditBase classes that can be saved."""

    def save(self, category=None):
        """Save the object.

        :param category: (Gold) The category to save to. If your user does not
            have gold this value is ignored by Reddit (default: None).

        Example usage:

        .. code:: python

           submission = reddit.submission(id='5or86n')
           submission.save(category="view later")

           comment = reddit.comment(id='dxolpyc')
           comment.save()

        See also :meth:`~.unsave`

        """
        self._reddit.post(
            API_PATH["save"], data={"category": category, "id": self.fullname}
        )

    def unsave(self):
        """Unsave the object.

        Example usage:

        .. code:: python

           submission = reddit.submission(id='5or86n')
           submission.unsave()

           comment = reddit.comment(id='dxolpyc')
           comment.unsave()

        See also :meth:`~.save`

        """
        self._reddit.post(API_PATH["unsave"], data={"id": self.fullname})
