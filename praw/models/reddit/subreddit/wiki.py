"""Provide the SubredditWiki class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from praw.const import API_PATH
from praw.models.reddit.subreddit.relationship import SubredditRelationship
from praw.models.reddit.wikipage import WikiPage

if TYPE_CHECKING:
    from collections.abc import Iterator

    from praw import models


class SubredditWiki:
    """Provides a set of wiki functions to a :class:`.Subreddit`."""

    def __getitem__(self, page_name: str) -> WikiPage:
        """Lazily return the :class:`.WikiPage` for the :class:`.Subreddit` named ``page_name``.

        This method is to be used to fetch a specific wikipage, like so:

        .. code-block:: python

            wikipage = reddit.subreddit("test").wiki["proof"]
            print(wikipage.content_md)

        """
        return WikiPage(self.subreddit._reddit, self.subreddit, page_name.lower())

    def __init__(self, subreddit: models.Subreddit) -> None:
        """Initialize a :class:`.SubredditWiki` instance.

        :param subreddit: The subreddit whose wiki to work with.

        """
        self.banned = SubredditRelationship(subreddit, "wikibanned")
        self.contributor = SubredditRelationship(subreddit, "wikicontributor")
        self.subreddit = subreddit

    def __iter__(self) -> Iterator[WikiPage]:
        """Iterate through the pages of the wiki.

        This method is to be used to discover all wikipages for a subreddit:

        .. code-block:: python

            for wikipage in reddit.subreddit("test").wiki:
                print(wikipage)

        """
        response = self.subreddit._reddit.get(
            API_PATH["wiki_pages"].format(subreddit=self.subreddit),
            params={"unique": self.subreddit._reddit._next_unique},
        )
        for page_name in response["data"]:
            yield WikiPage(self.subreddit._reddit, self.subreddit, page_name)

    def create(
        self,
        *,
        content: str,
        name: str,
        reason: str | None = None,
        **other_settings: Any,
    ) -> WikiPage:
        """Create a new :class:`.WikiPage`.

        :param name: The name of the new :class:`.WikiPage`. This name will be
            normalized.
        :param content: The content of the new :class:`.WikiPage`.
        :param reason: The reason for the creation.
        :param other_settings: Additional keyword arguments to pass.

        To create the wiki page ``"praw_test"`` in r/test try:

        .. code-block:: python

            reddit.subreddit("test").wiki.create(
                name="praw_test", content="wiki body text", reason="PRAW Test Creation"
            )

        """
        name = name.replace(" ", "_").lower()
        new = WikiPage(self.subreddit._reddit, self.subreddit, name)
        new.edit(content=content, reason=reason, **other_settings)
        return new

    def revisions(
        self, **generator_kwargs: Any
    ) -> Iterator[dict[str, models.Redditor | WikiPage | str | int | bool | None]]:
        """Return a :class:`.ListingGenerator` for recent wiki revisions.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        To view the wiki revisions for ``"praw_test"`` in r/test try:

        .. code-block:: python

            for item in reddit.subreddit("test").wiki["praw_test"].revisions():
                print(item)

        """
        url = API_PATH["wiki_revisions"].format(subreddit=self.subreddit)
        return WikiPage._revision_generator(generator_kwargs=generator_kwargs, subreddit=self.subreddit, url=url)
