"""Provide the SubredditFilters class."""

from json import dumps

from ....const import API_PATH


class SubredditFilters:
    """Provide functions to interact with the special Subreddit's filters.

    Members of this class should be utilized via ``Subreddit.filters``. For
    example, to add a filter, run:

    .. code-block:: python

        reddit.subreddit('all').filters.add('subreddit_name')

    """

    def __init__(self, subreddit):
        """Create a SubredditFilters instance.

        :param subreddit: The special subreddit whose filters to work with.

        As of this writing filters can only be used with the special subreddits
        ``all`` and ``mod``.

        """
        self.subreddit = subreddit

    def __iter__(self):
        """Iterate through the special subreddit's filters.

        This method should be invoked as:

        .. code-block:: python

           for subreddit in reddit.subreddit('NAME').filters:
               ...

        """
        url = API_PATH["subreddit_filter_list"].format(
            special=self.subreddit, user=self.subreddit._reddit.user.me()
        )
        params = {"unique": self.subreddit._reddit._next_unique}
        response_data = self.subreddit._reddit.get(url, params=params)
        for subreddit in response_data.subreddits:
            yield subreddit

    def add(self, subreddit):
        """Add ``subreddit`` to the list of filtered subreddits.

        :param subreddit: The subreddit to add to the filter list.

        Items from subreddits added to the filtered list will no longer be
        included when obtaining listings for ``r/all``.

        Alternatively, you can filter a subreddit temporarily from a special
        listing in a manner like so:

        .. code-block:: python

           reddit.subreddit('all-redditdev-learnpython')

        Raises ``prawcore.NotFound`` when calling on a non-special subreddit.

        """
        url = API_PATH["subreddit_filter"].format(
            special=self.subreddit,
            user=self.subreddit._reddit.user.me(),
            subreddit=subreddit,
        )
        self.subreddit._reddit.request(
            "PUT", url, data={"model": dumps({"name": str(subreddit)})}
        )

    def remove(self, subreddit):
        """Remove ``subreddit`` from the list of filtered subreddits.

        :param subreddit: The subreddit to remove from the filter list.

        Raises ``prawcore.NotFound`` when calling on a non-special subreddit.

        """
        url = API_PATH["subreddit_filter"].format(
            special=self.subreddit,
            user=self.subreddit._reddit.user.me(),
            subreddit=str(subreddit),
        )
        self.subreddit._reddit.request("DELETE", url, data={})
