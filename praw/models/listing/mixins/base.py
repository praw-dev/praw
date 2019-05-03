"""Provide the BaseListingMixin class."""
from ....compat import urljoin
from ...base import PRAWBase
from ..generator import ListingGenerator


def _prepare(praw_object, arguments_dict, target):
    """Fix for Redditor methods that use a query param rather than subpath."""
    if praw_object.__dict__.get("_listing_use_sort"):
        PRAWBase._safely_add_arguments(arguments_dict, "params", sort=target)
        return praw_object._path
    return urljoin(praw_object._path, target)


class BaseListingMixin(PRAWBase):
    """Adds minimum set of methods that apply to all listing objects."""

    VALID_TIME_FILTERS = {"all", "day", "hour", "month", "week", "year"}

    @staticmethod
    def _validate_time_filter(time_filter):
        """Raise :py:class:`.ValueError` if ``time_filter`` is not valid."""
        if time_filter not in BaseListingMixin.VALID_TIME_FILTERS:
            raise ValueError(
                "time_filter must be one of: {}".format(
                    ", ".join(BaseListingMixin.VALID_TIME_FILTERS)
                )
            )

    def controversial(self, time_filter="all", **generator_kwargs):
        """Return a ListingGenerator for controversial submissions.

        :param time_filter: Can be one of: all, day, hour, month, week, year
            (default: all).

        Raise :py:class:`.ValueError` if ``time_filter`` is invalid.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method can be used like:

        .. code:: python

           reddit.domain('imgur.com').controversial('week')
           reddit.multireddit('samuraisam', 'programming').controversial('day')
           reddit.redditor('spez').controversial('month')
           reddit.redditor('spez').comments.controversial('year')
           reddit.redditor('spez').submissions.controversial('all')
           reddit.subreddit('all').controversial('hour')

        """
        self._validate_time_filter(time_filter)
        self._safely_add_arguments(generator_kwargs, "params", t=time_filter)
        url = _prepare(self, generator_kwargs, "controversial")
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def hot(self, **generator_kwargs):
        """Return a ListingGenerator for hot items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method can be used like:

        .. code:: python

           reddit.domain('imgur.com').hot()
           reddit.multireddit('samuraisam', 'programming').hot()
           reddit.redditor('spez').hot()
           reddit.redditor('spez').comments.hot()
           reddit.redditor('spez').submissions.hot()
           reddit.subreddit('all').hot()

        """
        generator_kwargs.setdefault("params", {})
        url = _prepare(self, generator_kwargs, "hot")
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def new(self, **generator_kwargs):
        """Return a ListingGenerator for new items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method can be used like:

        .. code:: python

           reddit.domain('imgur.com').new()
           reddit.multireddit('samuraisam', 'programming').new()
           reddit.redditor('spez').new()
           reddit.redditor('spez').comments.new()
           reddit.redditor('spez').submissions.new()
           reddit.subreddit('all').new()

        """
        generator_kwargs.setdefault("params", {})
        url = _prepare(self, generator_kwargs, "new")
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def top(self, time_filter="all", **generator_kwargs):
        """Return a ListingGenerator for top submissions.

        :param time_filter: Can be one of: all, day, hour, month, week, year
            (default: all).

        Raise :py:class:`.ValueError` if ``time_filter`` is invalid.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method can be used like:

        .. code:: python

           reddit.domain('imgur.com').top('week')
           reddit.multireddit('samuraisam', 'programming').top('day')
           reddit.redditor('spez').top('month')
           reddit.redditor('spez').comments.top('year')
           reddit.redditor('spez').submissions.top('all')
           reddit.subreddit('all').top('hour')

        """
        self._validate_time_filter(time_filter)
        self._safely_add_arguments(generator_kwargs, "params", t=time_filter)
        url = _prepare(self, generator_kwargs, "top")
        return ListingGenerator(self._reddit, url, **generator_kwargs)
