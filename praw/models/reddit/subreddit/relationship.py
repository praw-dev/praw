"""Provide the SubredditRelationship class."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

from praw.const import API_PATH
from praw.models.listing.generator import ListingGenerator
from praw.models.reddit.base import RedditBase
from praw.models.util import permissions_string

if TYPE_CHECKING:
    from collections.abc import Iterator

    from praw import models


class SubredditRelationship:
    """Represents a relationship between a :class:`.Redditor` and :class:`.Subreddit`.

    Instances of this class can be iterated through in order to discover the Redditors
    that make up the relationship.

    For example, banned users of a subreddit can be iterated through like so:

    .. code-block:: python

        for ban in reddit.subreddit("test").banned():
            print(f"{ban}: {ban.note}")

    """

    def __call__(
        self,
        redditor: str | models.Redditor | None = None,
        **generator_kwargs: Any,
    ) -> Iterator[models.Redditor]:
        r"""Return a :class:`.ListingGenerator` for :class:`.Redditor`\ s in the relationship.

        :param redditor: When provided, yield at most a single :class:`.Redditor`
            instance. This is useful to confirm if a relationship exists, or to fetch
            the metadata associated with a particular relationship (default: ``None``).

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        """
        RedditBase._safely_add_arguments(arguments=generator_kwargs, key="params", user=redditor)
        url = API_PATH[f"list_{self.relationship}"].format(subreddit=self.subreddit)
        return ListingGenerator(self.subreddit._reddit, url, **generator_kwargs)

    def __init__(self, subreddit: models.Subreddit, relationship: str) -> None:
        """Initialize a :class:`.SubredditRelationship` instance.

        :param subreddit: The :class:`.Subreddit` for the relationship.
        :param relationship: The name of the relationship.

        """
        self.relationship = relationship
        self.subreddit = subreddit

    def add(self, redditor: str | models.Redditor, **other_settings: Any) -> None:
        """Add ``redditor`` to this relationship.

        :param redditor: A redditor name or :class:`.Redditor` instance.

        """
        data = {"name": str(redditor), "type": self.relationship}
        data.update(other_settings)
        url = API_PATH["friend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def remove(self, redditor: str | models.Redditor) -> None:
        """Remove ``redditor`` from this relationship.

        :param redditor: A redditor name or :class:`.Redditor` instance.

        """
        data = {"name": str(redditor), "type": self.relationship}
        url = API_PATH["unfriend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)


class ContributorRelationship(SubredditRelationship):
    r"""Provides methods to interact with a :class:`.Subreddit`'s contributors.

    Contributors are also known as approved submitters.

    Contributors of a subreddit can be iterated through like so:

    .. code-block:: python

        for contributor in reddit.subreddit("test").contributor():
            print(contributor)

    """

    def leave(self) -> None:
        """Abdicate the contributor position."""
        self.subreddit._reddit.post(API_PATH["leavecontributor"], data={"id": self.subreddit.fullname})


class ModeratorRelationship(SubredditRelationship):
    r"""Provides methods to interact with a :class:`.Subreddit`'s moderators.

    Moderators of a subreddit can be iterated through like so:

    .. code-block:: python

        for moderator in reddit.subreddit("test").moderator():
            print(moderator)

    """

    PERMISSIONS = frozenset({
        "access",
        "chat_config",
        "chat_operator",
        "config",
        "flair",
        "mail",
        "posts",
        "wiki",
    })

    @staticmethod
    def _handle_permissions(
        *,
        other_settings: dict | None = None,
        permissions: list[str] | None = None,
    ) -> dict[str, Any]:
        other_settings = deepcopy(other_settings) if other_settings else {}
        other_settings["permissions"] = permissions_string(
            known_permissions=set(ModeratorRelationship.PERMISSIONS), permissions=permissions
        )
        return other_settings

    def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]  # intentionally non-paginated; returns a list
        self, redditor: str | models.Redditor | None = None
    ) -> list[models.Redditor]:
        r"""Return a list of :class:`.Redditor`\ s who are moderators.

        :param redditor: When provided, return a list containing at most one
            :class:`.Redditor` instance. This is useful to confirm if a relationship
            exists, or to fetch the metadata associated with a particular relationship
            (default: ``None``).

        .. note::

            To help mitigate targeted moderator harassment, this call requires the
            :class:`.Reddit` instance to be authenticated i.e., :attr:`.read_only` must
            return ``False``. This call, however, only makes use of the ``read`` scope.
            For more information on why the moderator list is hidden can be found here:
            https://support.reddithelp.com/hc/en-us/articles/360049499032-Why-can-t-I-see-the-list-of-moderators-in-a-community-

        .. note::

            Unlike other relationship callables, this relationship is not paginated.
            Thus, it simply returns the full list, rather than an iterator for the
            results.

        To be used like:

        .. code-block:: python

            moderators = reddit.subreddit("test").moderator()

        For example, to list the moderators along with their permissions try:

        .. code-block:: python

            for moderator in reddit.subreddit("test").moderator():
                print(f"{moderator}: {moderator.mod_permissions}")

        """
        params: dict[str, str | int] = {} if redditor is None else {"user": str(redditor)}
        url = API_PATH[f"list_{self.relationship}"].format(subreddit=self.subreddit)
        return self.subreddit._reddit.get(url, params=params)

    def add(
        self,
        redditor: str | models.Redditor,
        *,
        permissions: list[str] | None = None,
        **other_settings: Any,
    ) -> None:
        """Add or invite ``redditor`` to be a moderator of the :class:`.Subreddit`.

        :param redditor: A redditor name or :class:`.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be a list
            of strings specifying which subset of permissions to grant. An empty list
            ``[]`` indicates no permissions, and when not provided ``None``, indicates
            full permissions (default: ``None``).

        An invite will be sent unless the user making this call is an admin user.

        For example, to invite u/spez with ``"posts"`` and ``"mail"`` permissions to
        r/test, try:

        .. code-block:: python

            reddit.subreddit("test").moderator.add("spez", permissions=["posts", "mail"])

        """
        other_settings = self._handle_permissions(other_settings=other_settings, permissions=permissions)
        super().add(redditor, **other_settings)

    def invite(
        self,
        redditor: str | models.Redditor,
        *,
        permissions: list[str] | None = None,
        **other_settings: Any,
    ) -> None:
        """Invite ``redditor`` to be a moderator of the :class:`.Subreddit`.

        :param redditor: A redditor name or :class:`.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be a list
            of strings specifying which subset of permissions to grant. An empty list
            ``[]`` indicates no permissions, and when not provided ``None``, indicates
            full permissions (default: ``None``).

        For example, to invite u/spez with ``"posts"`` and ``"mail"`` permissions to
        r/test, try:

        .. code-block:: python

            reddit.subreddit("test").moderator.invite("spez", permissions=["posts", "mail"])

        """
        data = self._handle_permissions(other_settings=other_settings, permissions=permissions)
        data.update({"name": str(redditor), "type": "moderator_invite"})
        url = API_PATH["friend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def invited(
        self,
        *,
        redditor: str | models.Redditor | None = None,
        **generator_kwargs: Any,
    ) -> Iterator[models.Redditor]:
        r"""Return a :class:`.ListingGenerator` for :class:`.Redditor`\ s invited to be moderators.

        :param redditor: When provided, return a list containing at most one
            :class:`.Redditor` instance. This is useful to confirm if a relationship
            exists, or to fetch the metadata associated with a particular relationship
            (default: ``None``).

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        .. note::

            Unlike other usages of :class:`.ListingGenerator`, ``limit`` has no effect
            in the quantity returned. This endpoint always returns moderators in batches
            of 25 at a time regardless of what ``limit`` is set to.

        Usage:

        .. code-block:: python

            for invited_mod in reddit.subreddit("test").moderator.invited():
                print(invited_mod)

        """
        generator_kwargs["params"] = {"username": redditor} if redditor else None
        url = API_PATH["list_invited_moderator"].format(subreddit=self.subreddit)
        return ListingGenerator(self.subreddit._reddit, url, **generator_kwargs)

    def leave(self) -> None:
        """Abdicate the moderator position (use with care).

        For example:

        .. code-block:: python

            reddit.subreddit("test").moderator.leave()

        """
        redditor = self.subreddit._reddit.config.username or self.subreddit._reddit.user.me()
        assert redditor is not None
        self.remove(redditor)

    def remove_invite(self, redditor: str | models.Redditor) -> None:
        """Remove the moderator invite for ``redditor``.

        :param redditor: A redditor name or :class:`.Redditor` instance.

        For example:

        .. code-block:: python

            reddit.subreddit("test").moderator.remove_invite("spez")

        """
        data = {"name": str(redditor), "type": "moderator_invite"}
        url = API_PATH["unfriend"].format(subreddit=self.subreddit)
        self.subreddit._reddit.post(url, data=data)

    def update(
        self,
        redditor: str | models.Redditor,
        *,
        permissions: list[str] | None = None,
    ) -> None:
        """Update the moderator permissions for ``redditor``.

        :param redditor: A redditor name or :class:`.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be a list
            of strings specifying which subset of permissions to grant. An empty list
            ``[]`` indicates no permissions, and when not provided, ``None``, indicates
            full permissions (default: ``None``).

        For example, to add all permissions to the moderator, try:

        .. code-block:: python

            subreddit.moderator.update("spez")

        To remove all permissions from the moderator, try:

        .. code-block:: python

            subreddit.moderator.update("spez", permissions=[])

        """
        url = API_PATH["setpermissions"].format(subreddit=self.subreddit)
        data = self._handle_permissions(
            other_settings={"name": str(redditor), "type": "moderator"},
            permissions=permissions,
        )
        self.subreddit._reddit.post(url, data=data)

    def update_invite(
        self,
        redditor: str | models.Redditor,
        *,
        permissions: list[str] | None = None,
    ) -> None:
        """Update the moderator invite permissions for ``redditor``.

        :param redditor: A redditor name or :class:`.Redditor` instance.
        :param permissions: When provided (not ``None``), permissions should be a list
            of strings specifying which subset of permissions to grant. An empty list
            ``[]`` indicates no permissions, and when not provided, ``None``, indicates
            full permissions (default: ``None``).

        For example, to grant the ``"flair"`` and ``"mail"`` permissions to the
        moderator invite, try:

        .. code-block:: python

            subreddit.moderator.update_invite("spez", permissions=["flair", "mail"])

        """
        url = API_PATH["setpermissions"].format(subreddit=self.subreddit)
        data = self._handle_permissions(
            other_settings={"name": str(redditor), "type": "moderator_invite"},
            permissions=permissions,
        )
        self.subreddit._reddit.post(url, data=data)
