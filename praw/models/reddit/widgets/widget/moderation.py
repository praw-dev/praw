"""Provide the WidgetModeration class."""

from json import dumps

from .....const import API_PATH
from ..encoder import WidgetEncoder


class WidgetModeration:
    """Class for moderating a particular widget.

    Example usage:

    .. code-block:: python

       widget = reddit.subreddit('my_sub').widgets.sidebar[0]
       widget.mod.update(shortName='My new title')
       widget.mod.delete()
    """

    def __init__(self, widget, subreddit, reddit):
        """Initialize the widget moderation object."""
        self.widget = widget
        self._reddit = reddit
        self._subreddit = subreddit

    def delete(self):
        """Delete the widget.

        Example usage:

        .. code-block:: python

           widget.mod.delete()
        """
        path = API_PATH["widget_modify"].format(
            widget_id=self.widget.id, subreddit=self._subreddit
        )
        self._reddit.request("DELETE", path)

    def update(self, **kwargs):
        """Update the widget. Returns the updated widget.

        Parameters differ based on the type of widget. See
        `Reddit documentation
        <https://www.reddit.com/dev/api#PUT_api_widget_{widget_id}>`_ or the
        document of the particular type of widget.
        For example, update a text widget like so:

        .. code-block:: python

           text_widget.mod.update(shortName='New text area', text='Hello!')

        .. note::

           Most parameters follow the ``lowerCamelCase`` convention. When in
           doubt, check the Reddit documentation linked above.
        """
        path = API_PATH["widget_modify"].format(
            widget_id=self.widget.id, subreddit=self._subreddit
        )
        payload = {
            key: value
            for key, value in vars(self.widget).items()
            if not key.startswith("_")
        }
        del payload["subreddit"]  # not JSON serializable
        payload.update(kwargs)
        widget = self._reddit.put(
            path, data={"json": dumps(payload, cls=WidgetEncoder)}
        )
        widget.subreddit = self._subreddit
        return widget
