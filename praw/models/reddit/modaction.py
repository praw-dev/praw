"""Provide the ModAction class."""

from .base import RedditBase


class ModAction(RedditBase):
    """A moderator action."""

    def __init__(self, reddit_session, json_dict=None, fetch=False):
        """Construct an instance of the ModAction object."""
        super(ModAction, self).__init__(reddit_session, json_dict, fetch)

    def __unicode__(self):
        """Return a string reprsentation of the moderator action."""
        return 'Action: {0}'.format(self.action)
