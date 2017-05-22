"""Provide the InboxToggleableMixin class."""
from ....const import API_PATH


class InboxToggleableMixin(object):
    """Interface for classes that can optionally receive inbox replies."""

    def disable_inbox_replies(self):
        """Disable inbox replies for the item."""
        self._reddit.post(API_PATH['sendreplies'], data={'id': self.fullname,
                                                         'state': False})

    def enable_inbox_replies(self):
        """Enable inbox replies for the item."""
        self._reddit.post(API_PATH['sendreplies'], data={'id': self.fullname,
                                                         'state': True})
