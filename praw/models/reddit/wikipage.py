"""Provide the WikiPage class."""
from typing import TYPE_CHECKING, Any, Dict, Generator, Iterator, Optional, Union

from ...const import API_PATH
from ...exceptions import MissingRequiredAttributeException
from ...util.cache import cachedproperty
from ..listing.generator import ListingGenerator
from .base import RedditBase
from .redditor import Redditor

if TYPE_CHECKING:  # pragma: no cover
    from .... import praw


class WikiPageModeration:
    """Provides a set of moderation functions for a WikiPage.

    For example, to add ``spez`` as an editor on the wikipage ``praw_test`` try:

    .. code-block:: python

        reddit.subreddit("test").wiki["praw_test"].mod.add("spez")

    """

    def __init__(self, wikipage: "WikiPage"):
        """Create a WikiPageModeration instance.

        :param wikipage: The wikipage to moderate.

        """
        self.wikipage = wikipage

    def _check_status(self) -> bool:
        """Check if a WikiPage revision is hidden or not.

        This method uses two API calls.

        """
        if not self.wikipage._revision:
            raise MissingRequiredAttributeException("Please specify a revision id.")
        before_list = list(
            self.wikipage.revisions(
                limit=1,
                params={
                    "before": f"WikiRevision_{self.wikipage._revision}",
                },
            )
        )
        if before_list:
            wiki_revision = next(
                self.wikipage.revisions(
                    limit=1,
                    params={
                        "after": f"WikiRevision_{before_list[0]['page']._revision}",
                    },
                )
            ).get("page")
            assert (
                wiki_revision._revision == self.wikipage._revision
            ), "Please file a bug report with PRAW."
            return wiki_revision.revision_hidden
        else:
            wiki_revision = next(self.wikipage.revisions(limit=1)).get("page")
            assert (
                wiki_revision._revision == self.wikipage._revision
            ), "Please file a bug report with PRAW."
            return wiki_revision.revision_hidden

    def add(self, redditor: "praw.models.Redditor"):
        """Add an editor to this WikiPage.

        :param redditor: A redditor name (e.g., ``"spez"``) or :class:`~.Redditor`
            instance.

        To add ``"spez"`` as an editor on the wikipage ``"praw_test"`` try:

        .. code-block:: python

            reddit.subreddit("test").wiki["praw_test"].mod.add("spez")

        """
        data = {"page": self.wikipage.name, "username": str(redditor)}
        url = API_PATH["wiki_page_editor"].format(
            subreddit=self.wikipage.subreddit, method="add"
        )
        self.wikipage._reddit.post(url, data=data)

    def hide(self, recheck: Optional[bool] = False) -> Dict[str, bool]:
        """Hide a WikiPage revision from public view.

        :param recheck: (boolean) Whether to check the visibility status of the revision
            even if the ``revision_hidden`` attribute is not ``None``. (default: False)

        :raises: :class:`.MissingRequiredAttributeException` if the WikiPage does not
            have a ``revision_id``.

        :returns: ``{'status': True}`` if the revision has been hidden.

        Example usage:

        .. code-block:: python

            for item in reddit.subreddit("test").wiki["test"].revisions(limit=10):
                wiki_page = item["page"]
                wiki_page.mod.hide()

        .. note::

            If the ``revision_hidden`` attribute of the instance of the WikiPage you are
            trying to hide is ``None``, or if the parameter ``recheck`` is true, this
            method will use two API calls to check if the revision is hidden. This
            procedure is used because the ``revision_hidden`` attribute is only present
            in listings of revisions. If the revision is visible, a third API call is
            used to hide the revision. Wiki revisions that are obtained from
            :meth:`~.WikiPage.revisions` have their ``revision_hidden`` attribute set on
            instantiation, and will not have their status checked unless the ``recheck``
            parameter is ``True``. The previous

            If revision ``[ID]`` of page ``test`` is visible, the following uses three
            API calls:

            .. code-block:: python

                wiki_page = reddit.subreddit("test").wiki["test"].revision("[ID]")
                wiki_page.mod.hide()

            You can use the :attr:`.revision_hidden` property to check the state of
            ``revision_hidden``.

        Hidden revisions are still visible to other moderators who have ``wiki``
        permissions.

        .. seealso::

            - :meth:`.unhide`
            - :meth:`.toggle_visibility`
            - :attr:`.revision_hidden`

        """
        if not self.wikipage._revision:
            raise MissingRequiredAttributeException("Please specify a revision id.")
        if self.wikipage.revision_hidden is None or recheck:
            self.wikipage.revision_hidden = self._check_status()
        if not self.wikipage.revision_hidden:
            return self.toggle_visibility()

    def remove(self, redditor: "praw.models.Redditor"):
        """Remove an editor from this WikiPage.

        :param redditor: A redditor name (e.g., ``"spez"``) or :class:`~.Redditor`
            instance.

        To remove ``"spez"`` as an editor on the wikipage ``"praw_test"`` try:

        .. code-block:: python

            reddit.subreddit("test").wiki["praw_test"].mod.remove("spez")

        """
        data = {"page": self.wikipage.name, "username": str(redditor)}
        url = API_PATH["wiki_page_editor"].format(
            subreddit=self.wikipage.subreddit, method="del"
        )
        self.wikipage._reddit.post(url, data=data)

    def revert(self):
        """Revert a wikipage back to a specific revision.

        To revert the page ``"praw_test"`` in ``r/test`` to revision ``[ID]``, try

        .. code-block:: python

            reddit.subreddit("test").wiki["praw_test"].revision("[ID]").mod.revert()

        .. note::

            When you attempt to revert the page ``config/stylesheet``, Reddit checks to
            see if the revision being reverted to passes the CSS filter. If the check
            fails, then the revision attempt will also fail. For example, you can't
            revert to a revision that contains a link to ``url(%%PRAW%%)`` if there is
            no image named ``PRAW`` on the current stylesheet.

            Here is an example of how to look for this type of error:

            .. code-block:: python

                from prawcore.exceptions import Forbidden

                try:
                    reddit.subreddit("test").wiki["config/stylesheet"].revision("[ID]").mod.revert()
                except Forbidden as exception:
                    exception.response.json()

        """
        self.wikipage._reddit.post(
            API_PATH["wiki_revert"].format(subreddit=self.wikipage.subreddit),
            data={
                "page": self.wikipage.name,
                "revision": self.wikipage._revision,
            },
        )

    def settings(self) -> Dict[str, Any]:
        """Return the settings for this WikiPage."""
        url = API_PATH["wiki_page_settings"].format(
            subreddit=self.wikipage.subreddit, page=self.wikipage.name
        )
        return self.wikipage._reddit.get(url)["data"]

    def toggle_visibility(self, set_status: Optional[bool] = True) -> Dict[str, bool]:
        """Toggle the public visibility of a wikipage revision.

        :param set_status: (boolean) Whether to set the ``revision_hidden`` attribute of
            the WikiPage revision after toggling the visibility. (Default: True)

        :raises: :class:`.MissingRequiredAttributeException` if the WikiPage does not
            have a ``revision_id``.

        :returns: ``{'status': True}`` if the revision has been hidden, and ``{'status':
            False}`` if the revision has been unhidden.

        To toggle the visibility of revision ``[ID]`` of ``"praw_test"`` in ``r/test``,
        try

        .. code-block:: python

            reddit.subreddit("test").wiki["praw_test"].revision("[ID]").mod.toggle_visibility()

        A hidden revision will still be visible to other moderators.

        .. seealso::

            - :meth:`.hide`
            - :meth:`.unhide`

        """
        if not self.wikipage._revision:
            raise MissingRequiredAttributeException("Please specify a revision id.")
        _visibility = self.wikipage._reddit.post(
            API_PATH["wiki_hide"].format(subreddit=self.wikipage.subreddit),
            data={
                "page": self.wikipage.name,
                "revision": self.wikipage._revision,
            },
        )
        if set_status:
            self.wikipage.revision_hidden = _visibility.get("status")
        return _visibility

    def unhide(self, recheck: Optional[bool] = False) -> Dict[str, bool]:
        """Make a WikiPage revision visible to the public.

        :param recheck: (boolean) Whether to check the visibility status of the revision
            even if the ``revision_hidden`` attribute is not ``None``. (default: False)

        :raises: :class:`.MissingRequiredAttributeException` if the WikiPage does not
            have a ``revision_id``.

        :returns: ``{'status': False}`` if the revision has been unhidden.

        Example usage:

        .. code-block:: python

            for item in reddit.subreddit("test").wiki["test"].revisions(limit=10):
                wiki_page = item["page"]
                wiki_page.mod.unhide()

        .. note::

            This method uses multiple API calls if the ``revision_hidden`` property is
            ``None``, or if the ``recheck`` parameter is set to ``True``. Confer the
            note on :meth:`.hide`.

        .. seealso::

            - :meth:`.hide`
            - :meth:`.toggle_visibility`
            - :attr:`.revision_hidden`

        """
        if not self.wikipage._revision:
            raise MissingRequiredAttributeException("Please specify a revision id.")
        if self.wikipage.revision_hidden is None or recheck:
            self.wikipage.revision_hidden = self._check_status()
        if self.wikipage.revision_hidden:
            return self.toggle_visibility()

    def update(
        self, listed: bool, permlevel: int, **other_settings: Any
    ) -> Dict[str, Any]:
        """Update the settings for this WikiPage.

        :param listed: (boolean) Show this page on page list.
        :param permlevel: (int) Who can edit this page? (0) use subreddit wiki
            permissions, (1) only approved wiki contributors for this page may edit (see
            :meth:`.WikiPageModeration.add`), (2) only mods may edit and view
        :param other_settings: Additional keyword arguments to pass.

        :returns: The updated WikiPage settings.

        To set the wikipage ``praw_test`` in ``r/test`` to mod only and disable it from
        showing in the page list, try:

        .. code-block:: python

            reddit.subreddit("test").wiki["praw_test"].mod.update(listed=False, permlevel=2)

        """
        other_settings.update({"listed": listed, "permlevel": permlevel})
        url = API_PATH["wiki_page_settings"].format(
            subreddit=self.wikipage.subreddit, page=self.wikipage.name
        )
        return self.wikipage._reddit.post(url, data=other_settings)["data"]


class WikiPage(RedditBase):
    """An individual WikiPage object.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this class.
    Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a guarantee that
    these attributes will always be present, nor is this list necessarily complete.

    =================== ===============================================================
    Attribute           Description
    =================== ===============================================================
    ``content_html``    The contents of the wiki page, as HTML.
    ``content_md``      The contents of the wiki page, as Markdown.
    ``may_revise``      A ``bool`` representing whether or not the authenticated user
                        may edit the wiki page.
    ``name``            The name of the wiki page.
    ``revision_by``     The :class:`~.Redditor` who authored this revision of the wiki
                        page.
    ``revision_date``   The time of this revision, in `Unix Time`_.
    ``revision_hidden`` A ``bool`` representing whether or not the wiki page is visible
                        to the public.
    ``subreddit``       The :class:`~.Subreddit` this wiki page belongs to.
    =================== ===============================================================

    .. _unix time: https://en.wikipedia.org/wiki/Unix_time

    """

    __hash__ = RedditBase.__hash__

    @staticmethod
    def _revision_generator(
        subreddit: "praw.models.Subreddit", url: str, generator_kwargs: Dict[str, Any]
    ) -> Generator[
        Dict[str, Optional[Union[Redditor, "WikiPage", str, int, bool]]], None, None
    ]:
        for revision in ListingGenerator(subreddit._reddit, url, **generator_kwargs):
            if revision["author"] is not None:
                revision["author"] = Redditor(
                    subreddit._reddit, _data=revision["author"]["data"]
                )
            revision["page"] = WikiPage(
                subreddit._reddit,
                subreddit,
                revision["page"],
                revision["id"],
                revision.get("revision_hidden"),
            )
            yield revision

    @cachedproperty
    def mod(self) -> WikiPageModeration:
        """Provide an instance of :class:`.WikiPageModeration`.

        For example, to add ``spez`` as an editor on the wikipage ``praw_test`` try:

        .. code-block:: python

            reddit.subreddit("test").wiki["praw_test"].mod.add("spez")

        """
        return WikiPageModeration(self)

    @property
    def revision_hidden(self) -> Union[bool, None]:
        """Check the ``revision_hidden`` attribute of a WikiPage revision.

        Example usage:

        .. code-block:: python

            one_revision = reddit.subreddit("test").wiki["praw"].revisions(limit=1)
            wiki_page = next(one_revision).get("page")
            wiki_page.revision_hidden

        To check and set the ``revision_hidden`` attribute of a WikiPage, try:

        .. code-block:: python

            wiki_page = reddit.subreddit("test").wiki["praw"].revision("[ID]")
            wiki_page.revision_hidden = wiki_page.mod._check_status()

        This does not change the visibility of the revision on Reddit.

        """
        return self._revision_hidden

    @revision_hidden.setter
    def revision_hidden(self, state):
        if not self._revision:
            raise MissingRequiredAttributeException("Please specify a revision id.")
        self._revision_hidden = state

    def __init__(
        self,
        reddit: "praw.Reddit",
        subreddit: "praw.models.Subreddit",
        name: str,
        revision: Optional[str] = None,
        revision_hidden: Optional[bool] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Construct an instance of the WikiPage object.

        :param revision: A specific revision ID to fetch. By default, fetches the most
            recent revision.

        """
        self.name = name
        self._revision = revision
        self._revision_hidden = revision_hidden
        self.subreddit = subreddit
        super().__init__(reddit, _data=_data, _str_field=False)

    def __repr__(self) -> str:
        """Return an object initialization representation of the instance."""
        return (
            f"{self.__class__.__name__}(subreddit={self.subreddit!r},"
            f" name={self.name!r})"
        )

    def __str__(self) -> str:
        """Return a string representation of the instance."""
        return f"{self.subreddit}/{self.name}"

    def _fetch_info(self):
        return (
            "wiki_page",
            {"subreddit": self.subreddit, "page": self.name},
            {"v": self._revision} if self._revision else None,
        )

    def _fetch_data(self):
        name, fields, params = self._fetch_info()
        path = API_PATH[name].format(**fields)
        return self._reddit.request("GET", path, params)

    def _fetch(self):
        data = self._fetch_data()
        data = data["data"]
        if data["revision_by"] is not None:
            data["revision_by"] = Redditor(
                self._reddit, _data=data["revision_by"]["data"]
            )
        self.__dict__.update(data)
        self._fetched = True

    def discussions(
        self, **generator_kwargs: Any
    ) -> Iterator["praw.models.Submission"]:
        """Return a :class:`.ListingGenerator` for discussions of a wiki page.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        Discussions are site-wide links to a wiki page.

        To view the titles of discussions of the page ``"praw_test"`` in ``r/test``,
        try:

        .. code-block:: python

            for submission in reddit.subreddit("test").wiki["praw_test"].discussions():
                print(submission.title)

        """
        return ListingGenerator(
            self._reddit,
            API_PATH["wiki_discussions"].format(
                subreddit=self.subreddit, page=self.name
            ),
            **generator_kwargs,
        )

    def edit(self, content: str, reason: Optional[str] = None, **other_settings: Any):
        """Edit this WikiPage's contents.

        :param content: The updated Markdown content of the page.
        :param reason: (Optional) The reason for the revision.
        :param other_settings: Additional keyword arguments to pass.

        For example, to replace the first wiki page of ``r/test`` with the phrase ``test
        wiki page``:

        .. code-block:: python

            page = next(iter(reddit.subreddit("test").wiki))
            page.edit(content="test wiki page")

        """
        other_settings.update({"content": content, "page": self.name, "reason": reason})
        self._reddit.post(
            API_PATH["wiki_edit"].format(subreddit=self.subreddit),
            data=other_settings,
        )

    def revision(self, revision: str):
        """Return a specific version of this page by revision ID.

        To view revision ``[ID]`` of ``"praw_test"`` in ``r/test``:

        .. code-block:: python

            page = reddit.subreddit("test").wiki["praw_test"].revision("[ID]")

        """
        return WikiPage(
            self.subreddit._reddit,
            self.subreddit,
            self.name,
            revision,
            self.revision_hidden,
        )

    def revisions(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Generator["WikiPage", None, None]:
        """Return a :class:`.ListingGenerator` for page revisions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To view the wiki revisions for ``"praw_test"`` in ``r/test`` try:

        .. code-block:: python

            for item in reddit.subreddit("test").wiki["praw_test"].revisions():
                print(item)

        To get :class:`.WikiPage` objects for each revision:

        .. code-block:: python

            for item in reddit.subreddit("test").wiki["praw_test"].revisions():
                print(item["page"])

        """
        url = API_PATH["wiki_page_revisions"].format(
            subreddit=self.subreddit, page=self.name
        )
        return self._revision_generator(self.subreddit, url, generator_kwargs)
