"""Provide the Subreddits class."""
from typing import Dict, Iterator, List, Optional, Union

from warnings import warn
from ..const import API_PATH
from . import Subreddit
from .base import PRAWBase
from .listing.generator import ListingGenerator
from .util import stream_generator


class Subreddits(PRAWBase):
    """Subreddits is a Listing class that provides various subreddit lists."""

    @staticmethod
    def _to_list(subreddit_list):
        return ",".join([str(x) for x in subreddit_list])

    def default(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator[Subreddit]:
        """Return a :class:`.ListingGenerator` for default subreddits.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.
        """
        return ListingGenerator(
            self._reddit, API_PATH["subreddits_default"], **generator_kwargs
        )

    def gold(self, **generator_kwargs) -> Iterator[Subreddit]:
        """Alias for :meth:`.premium` to maintain backwards compatibility."""
        warn(
            "`subreddits.gold` has be renamed to `subreddits.premium`.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.premium(**generator_kwargs)

    def premium(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator[Subreddit]:
        """Return a :class:`.ListingGenerator` for premium subreddits.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.
        """
        return ListingGenerator(
            self._reddit, API_PATH["subreddits_gold"], **generator_kwargs
        )

    def new(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator[Subreddit]:
        """Return a :class:`.ListingGenerator` for new subreddits.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.
        """
        return ListingGenerator(
            self._reddit, API_PATH["subreddits_new"], **generator_kwargs
        )

    def popular(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator[Subreddit]:
        """Return a :class:`.ListingGenerator` for popular subreddits.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.
        """
        return ListingGenerator(
            self._reddit, API_PATH["subreddits_popular"], **generator_kwargs
        )

    def recommended(
        self,
        subreddits: List[Union[str, Subreddit]],
        omit_subreddits: Optional[List[Union[str, Subreddit]]] = None,
    ) -> List[Subreddit]:
        """Return subreddits recommended for the given list of subreddits.

        :param subreddits: A list of Subreddit instances and/or subreddit
            names.
        :param omit_subreddits: A list of Subreddit instances and/or subreddit
            names to exclude from the results (Reddit's end may not work as
            expected).

        """
        if not isinstance(subreddits, list):
            raise TypeError("subreddits must be a list")
        if omit_subreddits is not None and not isinstance(omit_subreddits, list):
            raise TypeError("omit_subreddits must be a list or None")

        params = {"omit": self._to_list(omit_subreddits or [])}
        url = API_PATH["sub_recommended"].format(subreddits=self._to_list(subreddits))
        return [
            Subreddit(self._reddit, sub["sr_name"])
            for sub in self._reddit.get(url, params=params)
        ]

    def search(
        self, query: str, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator[Subreddit]:
        """Return a :class:`.ListingGenerator` of subreddits matching ``query``.

        Subreddits are searched by both their title and description.

        :param query: The query string to filter subreddits by.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        .. seealso:: :meth:`~.search_by_name` to search by subreddit names

        """
        self._safely_add_arguments(generator_kwargs, "params", q=query)
        return ListingGenerator(
            self._reddit, API_PATH["subreddits_search"], **generator_kwargs
        )

    def search_by_name(
        self, query: str, include_nsfw: bool = True, exact: bool = False
    ) -> List[Subreddit]:
        """Return list of Subreddits whose names begin with ``query``.

        :param query: Search for subreddits beginning with this string.
        :param include_nsfw: Include subreddits labeled NSFW (default: True).
        :param exact: Return only exact matches to ``query`` (default: False).

        """
        result = self._reddit.post(
            API_PATH["subreddits_name_search"],
            data={"include_over_18": include_nsfw, "exact": exact, "query": query},
        )
        return [self._reddit.subreddit(x) for x in result["names"]]

    def search_by_topic(self, query: str) -> List[Subreddit]:
        """Return list of Subreddits whose topics match ``query``.

        :param query: Search for subreddits relevant to the search topic.

        """
        result = self._reddit.get(
            API_PATH["subreddits_by_topic"], params={"query": query}
        )
        return [self._reddit.subreddit(x["name"]) for x in result if x.get("name")]

    def stream(
        self, **stream_options: Union[str, int, Dict[str, str]]
    ) -> Iterator[Subreddit]:
        """Yield new subreddits as they are created.

        Subreddits are yielded oldest first. Up to 100 historical subreddits
        will initially be returned.

        Keyword arguments are passed to :func:`.stream_generator`.

        """
        return stream_generator(self.new, **stream_options)
