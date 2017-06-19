"""Provide the WikiPage class."""
import json
from prawcore.exceptions import Conflict

from ...const import API_PATH
from ..listing.generator import ListingGenerator
from .base import RedditBase
from .redditor import Redditor


class WikiPage(RedditBase):
    """An individual WikiPage object."""

    @staticmethod
    def _revision_generator(subreddit, url, generator_kwargs):
        for revision in ListingGenerator(subreddit._reddit, url,
                                         **generator_kwargs):
            if revision['author'] is not None:
                revision['author'] = Redditor(subreddit._reddit,
                                              _data=revision['author']['data'])
            revision['page'] = WikiPage(subreddit._reddit, subreddit,
                                        revision['page'], revision['id'])
            yield revision

    @property
    def mod(self):
        """Provide an instance of :class:`.WikiPageModeration`."""
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

    def __init__(self, reddit, subreddit, name, revision=None, _data=None):
        """Construct an instance of the WikiPage object.

        :param revision: A specific revision ID to fetch. By default, fetches
            the most recent revision.

        """
        self.name = name
        self._revision = revision
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
        params = {'v': self._revision} if self._revision else None
        data = self._reddit.get(self._info_path(), params=params)['data']
        if data['revision_by'] is not None:
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

    def revisions(self, **generator_kwargs):
        """Return a generator for page revisions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To view the wiki revisions for ``'praw_test'`` in ``'/r/test'`` try:

        .. code:: python

           for item in reddit.subreddit('test').wiki['praw_test'].revisions():
               print(item)

        """
        url = API_PATH['wiki_page_revisions'].format(subreddit=self.subreddit,
                                                     page=self.name)
        return self._revision_generator(self.subreddit, url, generator_kwargs)

    def update(self, transformation, reason=None):
        """Safely update a page based on its current content.

        :param transformation: A function taking the previous content as its
            sole parameter and returning the new content.
        :param reason: (Optional) The reason for the revision.

        """
        current_revision = next(self.revisions(limit=1))
        revision_id = current_revision['id']
        content = current_revision['page'].content_md
        new_content = transformation(content)
        while True:
            try:
                self.edit(new_content, reason=reason, previous=revision_id)
                return
            except Conflict as conflict:
                response_body = json.loads(conflict.response.content.decode())
                new_content = transformation(response_body['newcontent'])
                revision_id = response_body['newrevision']


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
        data = {'page': self.wikipage.name, 'username': str(redditor)}
        url = API_PATH['wiki_page_editor'].format(
            subreddit=self.wikipage.subreddit, method='add')
        self.wikipage._reddit.post(url, data=data)

    def remove(self, redditor):
        """Remove an editor from this WikiPage.

        :param redditor: A redditor name (e.g., ``'spez'``) or
            :class:`~.Redditor` instance.

        To remove ``'spez'`` as an editor on the wikipage ``'praw_test'`` try:

        .. code:: python

           reddit.subreddit('test').wiki['praw_test'].mod.remove('spez')

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
        other_settings.update({'listed': listed, 'permlevel': permlevel})
        url = API_PATH['wiki_page_settings'].format(
            subreddit=self.wikipage.subreddit, page=self.wikipage.name)
        return self.wikipage._reddit.post(url, data=other_settings)['data']
