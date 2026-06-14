"""Provide the SubredditFilters class."""

from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING

from praw.const import API_PATH

if TYPE_CHECKING:
    from collections.abc import Iterator

    from praw import models


class SubredditFilters:
    """Provide functions to interact with the special :class:`.Subreddit`'s filters.

    Members of this class should be utilized via :meth:`.Subreddit.filters`. For
    example, to add a filter, run:

    .. code-block:: python

        reddit.subreddit("all").filters.add("test")

    """

    def __init__(self, subreddit: models.Subreddit) -> None:
        """Initialize a :class:`.SubredditFilters` instance.

        :param subreddit: The special subreddit whose filters to work with.

        As of this writing filters can only be used with the special subreddits ``all``
        and ``mod``.

        """
        self.subreddit = subreddit

    def __iter__(self) -> Iterator[models.Subreddit]:
        """Iterate through the special :class:`.Subreddit`'s filters.

        This method should be invoked as:

        .. code-block:: python

            for subreddit in reddit.subreddit("test").filters:
                ...

        """
        url = API_PATH["subreddit_filter_list"].format(special=self.subreddit, user=self.subreddit._reddit.user.me())
        params: dict[str, str | int] = {"unique": self.subreddit._reddit._next_unique}
        response_data = self.subreddit._reddit.get(url, params=params)
        yield from response_data.subreddits

    def add(self, subreddit: models.Subreddit | str) -> None:
        """Add ``subreddit`` to the list of filtered subreddits.

        :param subreddit: The subreddit to add to the filter list.

        Items from subreddits added to the filtered list will no longer be included when
        obtaining listings for r/all.

        Alternatively, you can filter a subreddit temporarily from a special listing in
        a manner like so:

        .. code-block:: python

            reddit.subreddit("all-redditdev-learnpython")

        :raises: ``prawcore.NotFound`` when calling on a non-special subreddit.

        """
        url = API_PATH["subreddit_filter"].format(
            special=self.subreddit,
            subreddit=subreddit,
            user=self.subreddit._reddit.user.me(),
        )
        self.subreddit._reddit.put(url, data={"model": dumps({"name": str(subreddit)})})

    def remove(self, subreddit: models.Subreddit | str) -> None:
        """Remove ``subreddit`` from the list of filtered subreddits.

        :param subreddit: The subreddit to remove from the filter list.

        :raises: ``prawcore.NotFound`` when calling on a non-special subreddit.

        """
        url = API_PATH["subreddit_filter"].format(
            special=self.subreddit,
            subreddit=str(subreddit),
            user=self.subreddit._reddit.user.me(),
        )
        self.subreddit._reddit.delete(url)
