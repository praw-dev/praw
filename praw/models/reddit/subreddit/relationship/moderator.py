"""Provide the ModeratorRelationship class."""

from copy import deepcopy

from .....const import API_PATH
from ....util import permissions_string
from .relationship import SubredditRelationship


class ModeratorRelationship(SubredditRelationship):
    """Provides methods to interact with a Subreddit's moderators.

    Moderators of a subreddit can be iterated through like so:

    .. code-block:: python

       for moderator in reddit.subreddit('redditdev').moderator():
           print(moderator)

    """

    PERMISSIONS = {"access", "config", "flair", "mail", "posts", "wiki"}

    @staticmethod
    def _handle_permissions(permissions, other_settings):
        other_settings = deepcopy(other_settings) if other_settings else {}
        other_settings["permissions"] = permissions_string(
            permissions, ModeratorRelationship.PERMISSIONS
        )
        return other_settings

    def __call__(self, redditor=None):  # pylint: disable=arguments-differ
        """Return a list of Redditors who are moderators.

        :param redditor: When provided, return a list containing at most one
            :class:`~.Redditor` instance. This is useful to confirm if a
            relationship exists, or to fetch the metadata associated with a
            particular relationship (default: None).

        .. note:: Unlike other relationship callables, this relationship is not
                  paginated. Thus it simply returns the full list, rather than
                  an iterator for the results.

        To be used like:

        .. code-block:: python

           moderators = reddit.subreddit('nameofsub').moderator()

        For example, to list the moderators along with their permissions try:

        .. code-block:: python

           for moderator in reddit.subreddit('SUBREDDIT').moderator():
               print('{}: {}'.format(moderator, moderator.mod_permissions))


        """
        params = {} if redditor is None else {"user": redditor}
        url = API_PATH["list_{}".format(self.relationship)].format(
            subreddit=self.subreddit
        )
        return self.subreddit._reddit.get(url, params=params)

    # pylint: disable=arguments-differ
    def add(self, redditor, permissions=None, **other_settings):
        """Add or invite ``redditor`` to be a moderator of the subreddit.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be
            a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when not
            provided ``None``, indicates full permissions.

        An invite will be sent unless the user making this call is an admin
        user.

        For example, to invite ``'spez'`` with ``'posts'`` and ``'mail'``
            permissions to ``r/test``, try:

        .. code-block:: python

           reddit.subreddit('test').moderator.add('spez', ['posts', 'mail'])

        """
        other_settings = self._handle_permissions(permissions, other_settings)
        super().add(redditor, **other_settings)

    # pylint: enable=arguments-differ

    def invite(self, redditor, permissions=None, **other_settings):
        """Invite ``redditor`` to be a moderator of the subreddit.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be
            a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when not
            provided ``None``, indicates full permissions.

        For example, to invite ``'spez'`` with ``posts`` and ``mail``
            permissions to ``r/test``, try:

        .. code-block:: python

           reddit.subreddit('test').moderator.invite('spez', ['posts', 'mail'])

        """
        data = self._handle_permissions(permissions, other_settings)
        data.update({"name": str(redditor), "type": "moderator_invite"})
        url = API_PATH["friend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def leave(self):
        """Abdicate the moderator position (use with care).

        For example:

        .. code-block:: python

           reddit.subreddit('subredditname').moderator.leave()

        """
        self.remove(self.subreddit._reddit.config.username)

    def remove_invite(self, redditor):
        """Remove the moderator invite for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        For example:

        .. code-block:: python

           reddit.subreddit('subredditname').moderator.remove_invite('spez')

        """
        data = {"name": str(redditor), "type": "moderator_invite"}
        url = API_PATH["unfriend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def update(self, redditor, permissions=None):
        """Update the moderator permissions for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be
            a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when not
            provided, ``None``, indicates full permissions.

        For example, to add all permissions to the moderator, try:

        .. code-block:: python

           subreddit.moderator.update('spez')

        To remove all permissions from the moderator, try:

        .. code-block:: python

           subreddit.moderator.update('spez', [])

        """
        url = API_PATH["setpermissions"].format(subreddit=self.subreddit)
        data = self._handle_permissions(
            permissions, {"name": str(redditor), "type": "moderator"}
        )
        self.subreddit._reddit.post(url, data=data)

    def update_invite(self, redditor, permissions=None):
        """Update the moderator invite permissions for ``redditor``.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be
            a list of strings specifying which subset of permissions to
            grant. An empty list ``[]`` indicates no permissions, and when not
            provided, ``None``, indicates full permissions.

        For example, to grant the ``flair``` and ``mail``` permissions to
        the moderator invite, try:

        .. code-block:: python

           subreddit.moderator.update_invite('spez', ['flair', 'mail'])

        """
        url = API_PATH["setpermissions"].format(subreddit=self.subreddit)
        data = self._handle_permissions(
            permissions, {"name": str(redditor), "type": "moderator_invite"}
        )
        self.subreddit._reddit.post(url, data=data)
