"""Provide the BaseListingMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

from praw.models.base import PRAWBase
from praw.models.listing.generator import ListingGenerator

if TYPE_CHECKING:
    from collections.abc import Iterator

    from typing_extensions import Unpack

    from praw.models.listing.generator import ListingGeneratorKwargs


class BaseListingMixin(PRAWBase):
    """Adds minimum set of methods that apply to all listing objects."""

    VALID_TIME_FILTERS = frozenset({"all", "day", "hour", "month", "week", "year"})

    if TYPE_CHECKING:
        _path: str

    @staticmethod
    def _validate_time_filter(time_filter: str) -> None:
        """Validate ``time_filter``.

        :raises: :py:class:`ValueError` if ``time_filter`` is not valid.

        """
        if time_filter not in BaseListingMixin.VALID_TIME_FILTERS:
            valid_time_filters = ", ".join(map("{!r}".format, BaseListingMixin.VALID_TIME_FILTERS))
            msg = f"'time_filter' must be one of: {valid_time_filters}"
            raise ValueError(msg)

    def _prepare(self, *, arguments: dict[str, Any], sort: str) -> str:
        """Fix for :class:`.Redditor` methods that use a query param rather than subpath."""
        if self.__dict__.get("_listing_use_sort"):
            self._safely_add_arguments(arguments=arguments, key="params", sort=sort)
            return self._path
        return urljoin(self._path, sort)

    def controversial(
        self,
        *,
        time_filter: str = "all",
        **generator_kwargs: Unpack[ListingGeneratorKwargs],
    ) -> Iterator[Any]:
        """Return a :class:`.ListingGenerator` for controversial items.

        :param time_filter: Can be one of: ``"all"``, ``"day"``, ``"hour"``,
            ``"month"``, ``"week"``, or ``"year"`` (default: ``"all"``).

        :raises: :py:class:`ValueError` if ``time_filter`` is invalid.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method can be used like:

        .. code-block:: python

            reddit.domain("imgur.com").controversial(time_filter="week")
            reddit.multireddit(redditor="samuraisam", name="programming").controversial(
                time_filter="day"
            )
            reddit.redditor("spez").controversial(time_filter="month")
            reddit.redditor("spez").comments.controversial(time_filter="year")
            reddit.redditor("spez").submissions.controversial(time_filter="all")
            reddit.subreddit("all").controversial(time_filter="hour")

        """
        self._validate_time_filter(time_filter)
        arguments: dict[str, Any] = dict(generator_kwargs)
        self._safely_add_arguments(arguments=arguments, key="params", t=time_filter)
        url = self._prepare(arguments=arguments, sort="controversial")
        return ListingGenerator(self._reddit, url, **arguments)

    def hot(self, **generator_kwargs: Unpack[ListingGeneratorKwargs]) -> Iterator[Any]:
        """Return a :class:`.ListingGenerator` for hot items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method can be used like:

        .. code-block:: python

            reddit.domain("imgur.com").hot()
            reddit.multireddit(redditor="samuraisam", name="programming").hot()
            reddit.redditor("spez").hot()
            reddit.redditor("spez").comments.hot()
            reddit.redditor("spez").submissions.hot()
            reddit.subreddit("all").hot()

        """
        arguments: dict[str, Any] = dict(generator_kwargs)
        arguments.setdefault("params", {})
        url = self._prepare(arguments=arguments, sort="hot")
        return ListingGenerator(self._reddit, url, **arguments)

    def new(self, **generator_kwargs: Unpack[ListingGeneratorKwargs]) -> Iterator[Any]:
        """Return a :class:`.ListingGenerator` for new items.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method can be used like:

        .. code-block:: python

            reddit.domain("imgur.com").new()
            reddit.multireddit(redditor="samuraisam", name="programming").new()
            reddit.redditor("spez").new()
            reddit.redditor("spez").comments.new()
            reddit.redditor("spez").submissions.new()
            reddit.subreddit("all").new()

        """
        arguments: dict[str, Any] = dict(generator_kwargs)
        arguments.setdefault("params", {})
        url = self._prepare(arguments=arguments, sort="new")
        return ListingGenerator(self._reddit, url, **arguments)

    def top(
        self,
        *,
        time_filter: str = "all",
        **generator_kwargs: Unpack[ListingGeneratorKwargs],
    ) -> Iterator[Any]:
        """Return a :class:`.ListingGenerator` for top items.

        :param time_filter: Can be one of: ``"all"``, ``"day"``, ``"hour"``,
            ``"month"``, ``"week"``, or ``"year"`` (default: ``"all"``).

        :raises: :py:class:`ValueError` if ``time_filter`` is invalid.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        This method can be used like:

        .. code-block:: python

            reddit.domain("imgur.com").top(time_filter="week")
            reddit.multireddit(redditor="samuraisam", name="programming").top(time_filter="day")
            reddit.redditor("spez").top(time_filter="month")
            reddit.redditor("spez").comments.top(time_filter="year")
            reddit.redditor("spez").submissions.top(time_filter="all")
            reddit.subreddit("all").top(time_filter="hour")

        """
        self._validate_time_filter(time_filter)
        arguments: dict[str, Any] = dict(generator_kwargs)
        self._safely_add_arguments(arguments=arguments, key="params", t=time_filter)
        url = self._prepare(arguments=arguments, sort="top")
        return ListingGenerator(self._reddit, url, **arguments)
