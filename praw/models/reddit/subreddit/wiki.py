"""Provide the SubredditWiki class."""

from ....const import API_PATH
from ..wikipage import WikiPage
from .relationship import SubredditRelationship


class SubredditWiki:
    """Provides a set of wiki functions to a Subreddit."""

    def __getitem__(self, page_name):
        """Lazily return the WikiPage for the subreddit named ``page_name``.

        This method is to be used to fetch a specific wikipage, like so:

        .. code-block:: python

           wikipage = reddit.subreddit('iama').wiki['proof']
           print(wikipage.content_md)

        """
        return WikiPage(
            self.subreddit._reddit, self.subreddit, page_name.lower()
        )

    def __init__(self, subreddit):
        """Create a SubredditWiki instance.

        :param subreddit: The subreddit whose wiki to work with.

        """
        self.banned = SubredditRelationship(subreddit, "wikibanned")
        self.contributor = SubredditRelationship(subreddit, "wikicontributor")
        self.subreddit = subreddit

    def __iter__(self):
        """Iterate through the pages of the wiki.

        This method is to be used to discover all wikipages for a subreddit:

        .. code-block:: python

           for wikipage in reddit.subreddit('iama').wiki:
               print(wikipage)

        """
        response = self.subreddit._reddit.get(
            API_PATH["wiki_pages"].format(subreddit=self.subreddit),
            params={"unique": self.subreddit._reddit._next_unique},
        )
        for page_name in response["data"]:
            yield WikiPage(self.subreddit._reddit, self.subreddit, page_name)

    def create(self, name, content, reason=None, **other_settings):
        """Create a new wiki page.

        :param name: The name of the new WikiPage. This name will be
            normalized.
        :param content: The content of the new WikiPage.
        :param reason: (Optional) The reason for the creation.
        :param other_settings: Additional keyword arguments to pass.

        To create the wiki page ``praw_test`` in ``r/test`` try:

        .. code-block:: python

           reddit.subreddit('test').wiki.create(
               'praw_test', 'wiki body text', reason='PRAW Test Creation')

        """
        name = name.replace(" ", "_").lower()
        new = WikiPage(self.subreddit._reddit, self.subreddit, name)
        new.edit(content=content, reason=reason, **other_settings)
        return new

    def revisions(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for recent wiki revisions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To view the wiki revisions for ``'praw_test'`` in ``r/test`` try:

        .. code-block:: python

           for item in reddit.subreddit('test').wiki['praw_test'].revisions():
               print(item)

        """
        url = API_PATH["wiki_revisions"].format(subreddit=self.subreddit)
        return WikiPage._revision_generator(
            self.subreddit, url, generator_kwargs
        )
