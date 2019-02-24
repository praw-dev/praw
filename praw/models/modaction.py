"""Provide the ModAction class."""

from .base import PRAWBase
from .reddit.redditor import Redditor


class ModAction(PRAWBase):
    """Represent a moderator action."""

    @property
    def mod(self):
        """Return the Redditor who the action was issued by."""
        return self._data['mod']

    @classmethod
    def _objectify_acknowledged(cls, reddit, data):
        key = 'mod'
        item = data.get(key)
        if isinstance(item, str):
            data[key] = Redditor(reddit, name=item)
        elif isinstance(item, Redditor):
            item._reddit = reddit

    def __init__(self, reddit, _data):
        """Initialize a ModAction instance."""
        if _data is not None:
            self._objectify_acknowledged(reddit, _data)
        super(ModAction, self).__init__(reddit, _data=_data)
