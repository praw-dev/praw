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

    def edit(self, content, reason=None, **other_settings):
        """Edit this wiki page's contents.

        :param content: The updated markdown content of the page.
        :param reason: The reason for the revision.
        :param **other_settings: Additional keyword arguments to pass.

        """
        other_settings.update({'content': content, 'page': self.name,
                               'reason': reason})
        self._reddit.post(API_PATH['wiki_edit'].format(
            subreddit=self.subreddit), data=other_settings)


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

    def update(self, listed, permlevel, **other_settings):
        """Update the settings for this wiki page.

        :param listed: (boolean) Show this page on page list.
        :param permlevel: (int) Who can edit this page? (0) use subreddit wiki
            permissions, (1) only approved wiki contributors for this page may
            edit (see `add`), (2) only mods may edit and view
        :param **other_settings: Additional keyword arguments to pass.
        :returns: The updated WikiPage settings.

        """
        other_settings.update({'listed': listed, 'permlevel': permlevel})
        url = API_PATH['wiki_page_settings'].format(
            subreddit=self.wikipage.subreddit, page=self.wikipage.name)
        return self.wikipage._reddit.post(url, data=other_settings)['data']
