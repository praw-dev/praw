"""Provide the GildableMixin class."""
from ....const import API_PATH


class GildableMixin(object):
    """Interface for classes that can be gilded."""

    def gild(self):
        """Gild the author of the item."""
        self._reddit.post(API_PATH['gild_thing'].format(
            fullname=self.fullname))
