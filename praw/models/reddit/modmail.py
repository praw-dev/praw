"""Provide models for new modmail."""
from ...const import API_PATH
from .base import RedditBase


class ModmailConversation(RedditBase):
    """A class for modmail conversations."""

    STR_FIELD = 'id'

    def __init__(self, reddit, id=None,  # pylint: disable=redefined-builtin
                 _data=None):
        """Construct an instance of the ModmailConversation object."""
        super(ModmailConversation, self).__init__(reddit, _data)

        if id is not None:
            self.id = id  # pylint: disable=invalid-name

    def _info_path(self):
        return API_PATH['modmail_conversation'].format(id=self.id)
