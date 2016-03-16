"""Provide the ModAction class."""

from .base import RedditBase


class ModAction(RedditBase):
    """A moderator action."""

    def __init__(self, reddit_session, json_dict=None, fetch=False):
        """Construct an instance of the ModAction object."""
        super(ModAction, self).__init__(reddit_session, json_dict, fetch)
