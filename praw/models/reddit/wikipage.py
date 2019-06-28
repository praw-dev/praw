"""Provide the WikiPage class."""
from ...const import API_PATH
from ...util.cache import cachedproperty
from ..listing.generator import ListingGenerator
from .base import RedditBase
from .redditor import Redditor


class WikiPage(RedditBase):
    """An individual WikiPage object.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily comprehensive.

    ======================= ===================================================
    Attribute               Description
    ======================= ===================================================
    ``content_html``        The contents of the wiki page, as HTML.
    ``content_md``          The contents of the wiki page, as Markdown.
    ``may_revise``          A ``bool`` representing whether or not the
                            authenticated user may edit the wiki page.
    ``name``                The name of the wiki page.
    ``revision_by``         The :class:`.Redditor` who authored this
                            revision of the wiki page.
    ``revision_date``       The time of this revision, in `Unix Time`_.
    ``subreddit``           The :class:`.Subreddit` this wiki page belongs to.
    ======================= ===================================================

    .. _Unix Time: https://en.wikipedia.org/wiki/Unix_time
    """

    __hash__ = RedditBase.__hash__

    @staticmethod
    def _revision_generator(subreddit, url, generator_kwargs):
        for revision in ListingGenerator(
            subreddit._reddit, url, **generator_kwargs
        ):
            if revision["author"] is not None:
                revision["author"] = Redditor(
                    subreddit._reddit, _data=revision["author"]["data"]
                )
            revision["page"] = WikiPage(
                subreddit._reddit, subreddit, revision["page"], revision["id"]
            )
            yield revision

    @cachedproperty
    def mod(self):
        """Provide an instance of :class:`.WikiPageModeration`."""
        return WikiPageModeration(self)

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        return (
            isinstance(other, self.__class__)
            and str(self).lower() == str(other).lower()
        )

    def __init__(self, reddit, subreddit, name, revision=None, _data=None):
        """Construct an instance of the WikiPage object.

        :param revision: A specific revision ID to fetch. By default, fetches
            the most recent revision.

        """
        self.name = name
        self._revision = revision
        self.subreddit = subreddit
        super(WikiPage, self).__init__(reddit, _data=_data)

    def __repr__(self):
        """Return an object initialization representation of the instance."""
        return "{}(subreddit={!r}, name={!r})".format(
            self.__class__.__name__, self.subreddit, self.name
        )

    def __str__(self):
        """Return a string representation of the instance."""
        return "{}/{}".format(self.subreddit, self.name)

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

    def edit(self, content, reason=None, **other_settings):
        """Edit this WikiPage's contents.

        :param content: The updated markdown content of the page.
        :param reason: (Optional) The reason for the revision.
        :param other_settings: Additional keyword arguments to pass.

        """
        other_settings.update(
            {"content": content, "page": self.name, "reason": reason}
        )
        self._reddit.post(
            API_PATH["wiki_edit"].format(subreddit=self.subreddit),
            data=other_settings,
        )

    def revision(self, revision):
        """Return a specific version of this page by revision ID.

        To view revision ``[ID]`` of ``'praw_test'`` in ``'/r/test'``:

        .. code:: python

           page = reddit.subreddit('test').wiki['praw_test'].revision('[ID]')

        """
        return WikiPage(
            self.subreddit._reddit, self.subreddit, self.name, revision
        )

    def revisions(self, **generator_kwargs):
        """Return a generator for page revisions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To view the wiki revisions for ``'praw_test'`` in ``'/r/test'`` try:

        .. code:: python

           for item in reddit.subreddit('test').wiki['praw_test'].revisions():
               print(item)

        To get :class:`.WikiPage` objects for each revision:

        .. code:: python

           for item in reddit.subreddit('test').wiki['praw_test'].revisions():
               print(item['page'])

        """
        url = API_PATH["wiki_page_revisions"].format(
            subreddit=self.subreddit, page=self.name
        )
        return self._revision_generator(self.subreddit, url, generator_kwargs)


class WikiPageModeration(object):
    """Provides a set of moderation functions for a WikiPage."""

    def __init__(self, wikipage):
        """Create a WikiPageModeration instance.

        :param wikipage: The wikipage to moderate.

        """
        self.wikipage = wikipage

    def add(self, redditor):
        """Add an editor to this WikiPage.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        To add ``'spez'`` as an editor on the wikipage ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('test').wiki['praw_test'].mod.add('spez')

        """
        data = {"page": self.wikipage.name, "username": str(redditor)}
        url = API_PATH["wiki_page_editor"].format(
            subreddit=self.wikipage.subreddit, method="add"
        )
        self.wikipage._reddit.post(url, data=data)

    def remove(self, redditor):
        """Remove an editor from this WikiPage.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        To remove ``'spez'`` as an editor on the wikipage ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('test').wiki['praw_test'].mod.remove('spez')

        """
        data = {"page": self.wikipage.name, "username": str(redditor)}
        url = API_PATH["wiki_page_editor"].format(
            subreddit=self.wikipage.subreddit, method="del"
        )
        self.wikipage._reddit.post(url, data=data)

    def settings(self):
        """Return the settings for this WikiPage."""
        url = API_PATH["wiki_page_settings"].format(
            subreddit=self.wikipage.subreddit, page=self.wikipage.name
        )
        return self.wikipage._reddit.get(url)["data"]

    def update(self, listed, permlevel, **other_settings):
        """Update the settings for this WikiPage.

        :param listed: (boolean) Show this page on page list.
        :param permlevel: (int) Who can edit this page? (0) use subreddit wiki
            permissions, (1) only approved wiki contributors for this page may
            edit (see :meth:`.WikiPageModeration.add`), (2) only mods may edit
            and view
        :param other_settings: Additional keyword arguments to pass.
        :returns: The updated WikiPage settings.

        To set the wikipage ``'praw_test'`` in ``'/r/test'`` to mod only and
          disable it from showing in the page list, try:

        .. code:: python

           reddit.subreddit('test').wiki['praw_test'].mod.update(listed=False,
                                                                 permlevel=2)

        """
        other_settings.update({"listed": listed, "permlevel": permlevel})
        url = API_PATH["wiki_page_settings"].format(
            subreddit=self.wikipage.subreddit, page=self.wikipage.name
        )
        return self.wikipage._reddit.post(url, data=other_settings)["data"]
