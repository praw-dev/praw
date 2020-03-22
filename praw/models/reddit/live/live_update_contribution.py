"""Provide the LiveThread class."""
from typing import TypeVar

from ....const import API_PATH

_LiveUpdate = TypeVar("_LiveUpdate")


class LiveUpdateContribution:
    """Provides a set of contribution functions to LiveUpdate."""

    def __init__(self, update: _LiveUpdate):
        """Create an instance of :class:`.LiveUpdateContribution`.

        :param update: An instance of :class:`.LiveUpdate`.

        This instance can be retrieved through ``update.contrib``
        where update is a :class:`.LiveUpdate` instance. E.g.,

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           update = thread['7827987a-c998-11e4-a0b9-22000b6a88d2']
           update.contrib  # LiveUpdateContribution instance
           update.contrib.remove()

        """
        self.update = update

    def remove(self):
        """Remove a live update.

        Usage:

         .. code-block:: python

           thread = reddit.live('ydwwxneu7vsa')
           update = thread['6854605a-efec-11e6-b0c7-0eafac4ff094']
           update.contrib.remove()

        """
        url = API_PATH["live_remove_update"].format(id=self.update.thread.id)
        data = {"id": self.update.fullname}
        self.update.thread._reddit.post(url, data=data)

    def strike(self):
        """Strike a content of a live update.

        .. code-block:: python

           thread = reddit.live('xyu8kmjvfrww')
           update = thread['cb5fe532-dbee-11e6-9a91-0e6d74fabcc4']
           update.contrib.strike()

        To check whether the update is stricken or not, use ``update.stricken``
        attribute. But note that accessing lazy attributes on updates
        (includes ``update.stricken``) may raises ``AttributeError``.
        See :class:`.LiveUpdate` for details.

        """
        url = API_PATH["live_strike"].format(id=self.update.thread.id)
        data = {"id": self.update.fullname}
        self.update.thread._reddit.post(url, data=data)
