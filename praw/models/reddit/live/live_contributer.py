"""Provide the LiveContributorRelationship class."""
from typing import List, Optional, TypeVar, Union

from ....const import API_PATH
from ...list.redditor import RedditorList
from ..redditor import Redditor

_LiveThread = TypeVar("_LiveThread")


class LiveContributorRelationship:
    """Provide methods to interact with live threads' contributors."""

    @staticmethod
    def _handle_permissions(permissions):
        if permissions is None:
            permissions = {"all"}
        else:
            permissions = set(permissions)
        return ",".join("+{}".format(x) for x in permissions)

    def __call__(self) -> List[Redditor]:
        """Return a :class:`.RedditorList` for live threads' contributors.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           for contributor in thread.contributor():
               print(contributor)

        """
        url = API_PATH["live_contributors"].format(id=self.thread.id)
        temp = self.thread._reddit.get(url)
        return temp if isinstance(temp, RedditorList) else temp[0]

    def __init__(self, thread: _LiveThread):
        """Create a :class:`.LiveContributorRelationship` instance.

        :param thread: An instance of :class:`.LiveThread`.

        .. note:: This class should not be initialized directly. Instead obtain
           an instance via: ``thread.contributor`` where ``thread`` is a
           :class:`.LiveThread` instance.

        """
        self.thread = thread

    def accept_invite(self):
        """Accept an invite to contribute the live thread.

        Usage:

        .. code-block:: python

            thread = reddit.live('ydwwxneu7vsa')
            thread.contributor.accept_invite()

        """
        url = API_PATH["live_accept_invite"].format(id=self.thread.id)
        self.thread._reddit.post(url)

    def invite(
        self,
        redditor: Union[str, Redditor],
        permissions: Optional[List[str]] = None,
    ):
        """Invite a redditor to be a contributor of the live thread.

        Raise :class:`.RedditAPIException` if the invitation already exists.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should
            be a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when
            not provided (``None``), indicates full permissions.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           redditor = reddit.redditor('spez')

           # 'manage' and 'settings' permissions
           thread.contributor.invite(redditor, ['manage', 'settings'])

        :seealso: :meth:`.LiveContributorRelationship.remove_invite` to
            remove the invite for redditor.

        """
        url = API_PATH["live_invite"].format(id=self.thread.id)
        data = {
            "name": str(redditor),
            "type": "liveupdate_contributor_invite",
            "permissions": self._handle_permissions(permissions),
        }
        self.thread._reddit.post(url, data=data)

    def leave(self):
        """Abdicate the live thread contributor position (use with care).

        Usage:

        .. code-block:: python

            thread = reddit.live('ydwwxneu7vsa')
            thread.contributor.leave()

        """
        url = API_PATH["live_leave"].format(id=self.thread.id)
        self.thread._reddit.post(url)

    def remove(self, redditor: Union[str, Redditor]):
        """Remove the redditor from the live thread contributors.

        :param redditor: A redditor fullname (e.g., ``'t2_1w72'``) or
            :class:`~.Redditor` instance.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           redditor = reddit.redditor('spez')
           thread.contributor.remove(redditor)
           thread.contributor.remove('t2_1w72')  # with fullname

        """
        if isinstance(redditor, Redditor):
            fullname = redditor.fullname
        else:
            fullname = redditor
        data = {"id": fullname}
        url = API_PATH["live_remove_contrib"].format(id=self.thread.id)
        self.thread._reddit.post(url, data=data)

    def remove_invite(self, redditor: Union[str, Redditor]):
        """Remove the invite for redditor.

        :param redditor: A redditor fullname (e.g., ``'t2_1w72'``) or
            :class:`~.Redditor` instance.

        Usage:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           redditor = reddit.redditor('spez')
           thread.contributor.remove_invite(redditor)
           thread.contributor.remove_invite('t2_1w72')  # with fullname

        :seealso: :meth:`.LiveContributorRelationship.invite` to
            invite a redditor to be a contributor of the live thread.

        """
        if isinstance(redditor, Redditor):
            fullname = redditor.fullname
        else:
            fullname = redditor
        data = {"id": fullname}
        url = API_PATH["live_remove_invite"].format(id=self.thread.id)
        self.thread._reddit.post(url, data=data)

    def update(
        self,
        redditor: Union[str, Redditor],
        permissions: Optional[List[str]] = None,
    ):
        """Update the contributor permissions for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should
            be a list of strings specifying which subset of permissions to
            grant (other permissions are removed). An empty list ``[]``
            indicates no permissions, and when not provided (``None``),
            indicates full permissions.

        For example, to grant all permissions to the contributor, try:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contributor.update('spez')

        To grant 'access' and 'edit' permissions (and to remove other
        permissions), try:

        .. code-block:: python

           thread.contributor.update('spez', ['access', 'edit'])

        To remove all permissions from the contributor, try:

        .. code-block:: python

           subreddit.moderator.update('spez', [])

        """
        url = API_PATH["live_update_perms"].format(id=self.thread.id)
        data = {
            "name": str(redditor),
            "type": "liveupdate_contributor",
            "permissions": self._handle_permissions(permissions),
        }
        self.thread._reddit.post(url, data=data)

    def update_invite(
        self,
        redditor: Union[str, Redditor],
        permissions: Optional[List[str]] = None,
    ):
        """Update the contributor invite permissions for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should
            be a list of strings specifying which subset of permissions to
            grant (other permissions are removed). An empty list ``[]``
            indicates no permissions, and when not provided (``None``),
            indicates full permissions.

        For example, to set all permissions to the invitation, try:

        .. code-block:: python

           thread = reddit.live('ukaeu1ik4sw5')
           thread.contributor.update_invite('spez')

        To set 'access' and 'edit' permissions (and to remove other
        permissions) to the invitation, try:

        .. code-block:: python

           thread.contributor.update_invite('spez', ['access', 'edit'])

        To remove all permissions from the invitation, try:

        .. code-block:: python

           thread.contributor.update_invite('spez', [])

        """
        url = API_PATH["live_update_perms"].format(id=self.thread.id)
        data = {
            "name": str(redditor),
            "type": "liveupdate_contributor_invite",
            "permissions": self._handle_permissions(permissions),
        }
        self.thread._reddit.post(url, data=data)
