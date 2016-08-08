"""Provide the WikiPage class."""
from ...const import API_PATH
from .base import RedditBase
from .redditor import Redditor


class WikiPage(RedditBase):
    """An individual WikiPage object."""

    @property
    def mod(self):
        """An instance of :class:`.WikiPageModeration`."""
        if self._mod is None:
            self._mod = WikiPageModeration(self)
        return self._mod

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
        self._mod = None

    def __repr__(self):
        """Return an object initialization representation of the instance."""
        return '{}(subreddit={!r}, name={!r})'.format(
            self.__class__.__name__, self.subreddit, self.name)

    def __str__(self):
        """Return a string representation of the instance."""
        return '{}/{}'.format(self.subreddit, self.name)

    def _fetch(self):
        data = self._reddit.get(self._info_path())['data']
        data['revision_by'] = Redditor(self._reddit,
                                       _data=data['revision_by']['data'])
        self.__dict__.update(data)
        self._fetched = True

    def _info_path(self):
        return API_PATH['wiki_page'].format(subreddit=self.subreddit,
                                            page=self.name)

    def edit(self, content, reason=None, **other_settings):
        """Edit this WikiPage's contents.

        :param content: The updated markdown content of the page.
        :param reason: (Optional) The reason for the revision.
        :param other_settings: Additional keyword arguments to pass.

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
        """Add an editor to this WikiPage.

        :param redditor: A string or :class:`~.Redditor` instance.

        """
        data = {'page': self.wikipage.name, 'username': str(redditor)}
        url = API_PATH['wiki_page_editor'].format(
            subreddit=self.wikipage.subreddit, method='add')
        self.wikipage._reddit.post(url, data=data)

    def remove(self, redditor):
        """Remove an editor from this WikiPage.

        :param redditor: A string or :class:`~.Redditor` instance.

        """
        data = {'page': self.wikipage.name, 'username': str(redditor)}
        url = API_PATH['wiki_page_editor'].format(
            subreddit=self.wikipage.subreddit, method='del')
        self.wikipage._reddit.post(url, data=data)

    def settings(self):
        """Return the settings for this WikiPage."""
        url = API_PATH['wiki_page_settings'].format(
            subreddit=self.wikipage.subreddit, page=self.wikipage.name)
        return self.wikipage._reddit.get(url)['data']

    def update(self, listed, permlevel, **other_settings):
        """Update the settings for this WikiPage.

        :param listed: (boolean) Show this page on page list.
        :param permlevel: (int) Who can edit this page? (0) use subreddit wiki
            permissions, (1) only approved wiki contributors for this page may
            edit (see `add`), (2) only mods may edit and view
        :param other_settings: Additional keyword arguments to pass.
        :returns: The updated WikiPage settings.

        """
        other_settings.update({'listed': listed, 'permlevel': permlevel})
        url = API_PATH['wiki_page_settings'].format(
            subreddit=self.wikipage.subreddit, page=self.wikipage.name)
        return self.wikipage._reddit.post(url, data=other_settings)['data']
