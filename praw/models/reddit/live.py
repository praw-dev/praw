"""Provide the LiveThread class."""
from ...const import API_PATH
from .base import RedditBase


class LiveThread(RedditBase):
    """An individual LiveThread object."""

    STR_FIELD = 'id'

    def _info_path(self):
        return API_PATH['liveabout'].format(id=self.id)
