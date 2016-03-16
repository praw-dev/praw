"""Provide the WikiPage class."""

from six import text_type

from .base import RedditBase


class WikiPage(RedditBase):
    """An individual WikiPage object."""

    @classmethod
    def from_api_response(cls, reddit_session, json_dict):
        """Return an instance of the appropriate class from the json_dict."""
        # The WikiPage response does not contain the necessary information
        # in the JSON response to determine the name of the page nor the
        # subreddit it belongs to. Thus we must extract this information
        # from the request URL.
        parts = reddit_session._request_url.split('/', 6)
        subreddit = parts[4]
        page = parts[6].split('.', 1)[0]
        return cls(reddit_session, subreddit, page, json_dict=json_dict)

    def __init__(self, reddit_session, subreddit=None, page=None,
                 json_dict=None, fetch=False, **kwargs):
        """Construct an instance of the WikiPage object."""
        if not subreddit and not page:
            subreddit = json_dict['sr']
            page = json_dict['page']
        info_url = reddit_session.config['wiki_page'].format(
            subreddit=text_type(subreddit), page=page)
        super(WikiPage, self).__init__(reddit_session, json_dict, fetch,
                                       info_url, **kwargs)
        self.page = page
        self.subreddit = subreddit

    def add_editor(self, username, _delete=False, *args, **kwargs):
        """Add an editor to this wiki page.

        :param username: The name or Redditor object of the user to add.
        :param _delete: If True, remove the user as an editor instead.
            Please use :meth:`remove_editor` rather than setting it manually.

        Additional parameters are passed into
        :meth:`~praw.__init__.BaseReddit.request_json`.
        """
        url = self.reddit_session.config['wiki_page_editor']
        url = url.format(subreddit=text_type(self.subreddit),
                         method='del' if _delete else 'add')

        data = {'page': self.page, 'username': text_type(username)}
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
            subreddit=text_type(self.subreddit), page=self.page)
        return self.reddit_session.request_json(url, *args, **kwargs)['data']

    def edit(self, *args, **kwargs):
        """Edit the wiki page.

        Convenience function that utilizes
        :meth:`.AuthenticatedReddit.edit_wiki_page` populating both the
        ``subreddit`` and ``page`` parameters.
        """
        return self.subreddit.edit_wiki_page(self.page, *args, **kwargs)

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
            subreddit=text_type(self.subreddit), page=self.page)
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
