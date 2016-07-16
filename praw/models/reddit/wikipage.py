"""Provide the WikiPage class."""
from ...const import API_PATH
from .base import RedditBase


class WikiPage(RedditBase):
    """An individual WikiPage object."""

    def __eq__(self, other):
        """Return whether the other instance equals the current."""
        return isinstance(other, self.__class__) and \
            str(self).lower() == str(other).lower()

    def __hash__(self):
        """Return the hash of the current instance."""
        return super(WikiPage, self).__hash__()

    def __init__(self, reddit, subreddit, name, _data=None):
        """Construct an instance of the WikiPage object."""
        self.name = name
        self.subreddit = subreddit
        super(WikiPage, self).__init__(reddit, _data)

    def __repr__(self):
        """Return an object initialization representation of the instance."""
        return '{}(subreddit={!r}, name={!r})'.format(
            self.__class__.__name__, self.subreddit, self.name)

    def __str__(self):
        """Return a string representation of the instance."""
        return '{}/{}'.format(self.subreddit, self.name)

    def _fetch(self):
        data = self._reddit.get(self._info_path())['data']
        self.__dict__.update(data)
        self._fetched = True

    def _info_path(self):
        return API_PATH['wiki_page'].format(subreddit=self.subreddit,
                                            page=self.name)

    def add_editor(self, username, _delete=False, *args, **kwargs):
        """Add an editor to this wiki page.

        :param username: The name or Redditor object of the user to add.
        :param _delete: If True, remove the user as an editor instead.
            Please use :meth:`remove_editor` rather than setting it manually.

        Additional parameters are passed into
        :meth:`~praw.__init__.BaseReddit.request_json`.
        """
        url = self.reddit_session.config['wiki_page_editor']
        url = url.format(subreddit=self.subreddit,
                         method='del' if _delete else 'add')

        data = {'page': self.name, 'username': str(username)}
        return self.reddit_session.request_json(url, data=data, *args,
                                                **kwargs)

    def get_settings(self, *args, **kwargs):
        """Return the settings for this wiki page.

        Includes permission level, names of editors, and whether
        the page is listed on /wiki/pages.

        Additional parameters are passed into
        :meth:`~praw.__init__.BaseReddit.request_json`
        """
        url = self.reddit_session.config['wiki_page_settings'].format(
            subreddit=self.subreddit, page=self.name)
        return self.reddit_session.request_json(url, *args, **kwargs)['data']

    def edit(self, *args, **kwargs):
        """Edit the wiki page.

        Convenience function that utilizes
        :meth:`.AuthenticatedReddit.edit_wiki_page` populating both the
        ``subreddit`` and ``page`` parameters.
        """
        return self.subreddit.edit_wiki_page(self.name, *args, **kwargs)

    def edit_settings(self, permlevel, listed, *args, **kwargs):
        """Edit the settings for this individual wiki page.

        :param permlevel: Who can edit this page?
            (0) use subreddit wiki permissions, (1) only approved wiki
            contributors for this page may edit (see
            :meth:`~praw.objects.WikiPage.add_editor`), (2) only mods may edit
            and view
        :param listed: Show this page on the listing?
            True - Appear in /wiki/pages
            False - Do not appear in /wiki/pages
        :returns: The updated settings data.

        Additional parameters are passed into :meth:`request_json`.

        """
        url = self.reddit_session.config['wiki_page_settings'].format(
            subreddit=self.subreddit, page=self.page)
        data = {'permlevel': permlevel,
                'listed': 'on' if listed else 'off'}

        return self.reddit_session.request_json(url, data=data, *args,
                                                **kwargs)['data']

    def remove_editor(self, username, *args, **kwargs):
        """Remove an editor from this wiki page.

        :param username: The name or Redditor object of the user to remove.

        This method points to :meth:`add_editor` with _delete=True.

        Additional parameters are are passed to :meth:`add_editor` and
        subsequently into :meth:`~praw.__init__.BaseReddit.request_json`.
        """
        return self.add_editor(username=username, _delete=True, *args,
                               **kwargs)
