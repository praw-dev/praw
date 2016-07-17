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
        self.mod = WikiPageModeration(self)
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


class WikiPageModeration(object):
    """Provides a set of moderation functions for a WikiPage."""

    def __init__(self, wikipage):
        """Create a WikiPageModeration instance.

        :param wikipage: The wikipage to moderate.

        """
        self.wikipage = wikipage

    def add(self, redditor):
        """Add an editor to this wiki page.

        :param redditor: A string or :class:`~.Redditor` instance.

        """
        data = {'page': self.wikipage.name, 'username': str(redditor)}
        url = API_PATH['wiki_page_editor'].format(
            subreddit=self.wikipage.subreddit, method='add')
        self.wikipage._reddit.post(url, data=data)

    def remove(self, redditor):
        """Remove an editor from this wiki page.

        :param redditor: A string or :class:`~.Redditor` instance.

        """
        data = {'page': self.wikipage.name, 'username': str(redditor)}
        url = API_PATH['wiki_page_editor'].format(
            subreddit=self.wikipage.subreddit, method='del')
        self.wikipage._reddit.post(url, data=data)

    def settings(self):
        """Return the settings for this wiki page."""
        url = API_PATH['wiki_page_settings'].format(
            subreddit=self.wikipage.subreddit, page=self.wikipage.name)
        return self.wikipage._reddit.get(url)['data']
