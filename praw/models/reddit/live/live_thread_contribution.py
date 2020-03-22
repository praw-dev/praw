"""Provide the LiveThread class."""
from typing import Optional, TypeVar

from ....const import API_PATH

_LiveThread = TypeVar("_LiveThread")


class LiveThreadContribution:
    """Provides a set of contribution functions to a LiveThread."""

    def __init__(self, thread: _LiveThread):
        """Create an instance of :class:`.LiveThreadContribution`.

        :param thread: An instance of :class:`.LiveThread`.

        This instance can be retrieved through ``thread.contrib``
        where thread is a :class:`.LiveThread` instance. E.g.,

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contrib.add('### update')

        """
        self.thread = thread

    def add(self, body: str):
        """Add an update to the live thread.

        :param body: The Markdown formatted content for the update.

        Usage:

        .. code-block:: python

           thread = reddit.live('ydwwxneu7vsa')
           thread.contrib.add('test `LiveThreadContribution.add()`')

        """
        url = API_PATH["live_add_update"].format(id=self.thread.id)
        self.thread._reddit.post(url, data={"body": body})

    def close(self):
        """Close the live thread permanently (cannot be undone).

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contrib.close()

        """
        url = API_PATH["live_close"].format(id=self.thread.id)
        self.thread._reddit.post(url)

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        nsfw: Optional[bool] = None,
        resources: Optional[str] = None,
        **other_settings: Optional[str]
    ):
        """Update settings of the live thread.

        :param title: (Optional) The title of the live thread (default: None).
        :param description: (Optional) The live thread's description
            (default: None).
        :param nsfw: (Optional) Indicate whether this thread is not safe for
            work (default: None).
        :param resources: (Optional) Markdown formatted information that is
            useful for the live thread (default: None).

        Does nothing if no arguments are provided.

        Each setting will maintain its current value if ``None`` is specified.

        Additional keyword arguments can be provided to handle new settings as
        Reddit introduces them.

        Usage:

        .. code-block:: python

           thread = reddit.live('xyu8kmjvfrww')

           # update `title` and `nsfw`
           updated_thread = thread.contrib.update(title=new_title, nsfw=True)

        If Reddit introduces new settings, you must specify ``None`` for the
        setting you want to maintain:

        .. code-block:: python

           # update `nsfw` and maintain new setting `foo`
           thread.contrib.update(nsfw=True, foo=None)

        """
        settings = {
            "title": title,
            "description": description,
            "nsfw": nsfw,
            "resources": resources,
        }
        settings.update(other_settings)
        if all(value is None for value in settings.values()):
            return
        # get settings from Reddit (not cache)
        thread = self.thread.__class__(self.thread._reddit, self.thread.id)
        data = {
            key: getattr(thread, key) if value is None else value
            for key, value in settings.items()
        }

        url = API_PATH["live_update_thread"].format(id=self.thread.id)
        # prawcore (0.7.0) Session.request() modifies `data` kwarg
        self.thread._reddit.post(url, data=data.copy())
        self.thread._reset_attributes(*data.keys())
