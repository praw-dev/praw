"""Provide the Widget class."""

from ....base import PRAWBase
from .moderation import WidgetModeration


class Widget(PRAWBase):
    """Base class to represent a Widget."""

    @property
    def mod(self):
        """Get an instance of :class:`.WidgetModeration` for this widget.

        .. note::
           Using any of the methods of :class:`.WidgetModeration` will likely
           make outdated the data in the :class:`.SubredditWidgets` that this
           widget belongs to. To remedy this, call
           :meth:`~.SubredditWidgets.refresh`.
        """
        if self._mod is None:
            self._mod = WidgetModeration(self, self.subreddit, self._reddit)
        return self._mod

    def __eq__(self, other):
        """Check equality against another object."""
        if isinstance(other, Widget):
            return self.id.lower() == other.id.lower()
        return str(other).lower() == self.id.lower()

    # pylint: disable=invalid-name
    def __init__(self, reddit, _data):
        """Initialize an instance of the class."""
        self.subreddit = ""  # in case it isn't in _data
        self.id = ""  # in case it isn't in _data
        super().__init__(reddit, _data=_data)
        self._mod = None
