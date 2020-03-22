"""Provide the WidgetEncoder class."""

from json import JSONEncoder
from ...base import PRAWBase


class WidgetEncoder(JSONEncoder):
    """Class to encode widget-related objects."""

    def default(self, o):  # pylint: disable=E0202
        """Serialize ``PRAWBase`` objects."""
        if isinstance(o, self._subreddit_class):
            return str(o)
        elif isinstance(o, PRAWBase):
            return {
                key: val
                for key, val in vars(o).items()
                if not key.startswith("_")
            }
        return JSONEncoder.default(self, o)
