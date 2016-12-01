"""Provide the Subreddits class."""
from . import Subreddit
from .base import PRAWBase
from .listing.generator import ListingGenerator
from .util import stream_generator
from ..const import API_PATH


class Subreddits(PRAWBase):
    """Subreddits is a Listing class that provides various subreddit lists."""

    def default(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for default subreddits."""
        return ListingGenerator(self._reddit, API_PATH['subreddits_default'],
                                **generator_kwargs)

    def gold(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for gold subreddits."""
        return ListingGenerator(self._reddit, API_PATH['subreddits_gold'],
                                **generator_kwargs)

    def new(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for new subreddits."""
        return ListingGenerator(self._reddit, API_PATH['subreddits_new'],
                                **generator_kwargs)

    def popular(self, **generator_kwargs):
        """Return a :class:`.ListingGenerator` for popular subreddits."""
        return ListingGenerator(self._reddit, API_PATH['subreddits_popular'],
                                **generator_kwargs)

    def recommended(self, subreddits, omit_subreddits=None):
        """Return subreddits recommended for the given list of subreddits.

        :param subreddits: A list of Subreddit instances and/or subreddit
            names.
        :param omit_subreddits: A list of Subreddit instances and/or subreddit
            names to exclude from the results (Reddit's end may not work as
            expected).

        """
        def _to_list(subreddit_list):
            return ','.join([str(x) for x in subreddit_list])

        if not isinstance(subreddits, list):
            raise TypeError('subreddits must be a list')
        if omit_subreddits is not None and \
           not isinstance(omit_subreddits, list):
            raise TypeError('omit_subreddits must be a list or None')

        params = {'omit': _to_list(omit_subreddits or [])}
        url = API_PATH['sub_recommended'].format(
            subreddits=_to_list(subreddits))
        return [Subreddit(self._reddit, sub['sr_name']) for sub in
                self._reddit.get(url, params=params)]

    def search(self, query, **generator_kwargs):
        """Return a :class:`.ListingGenerator` of subreddits matching ``query``.

        Subreddits are searched by both their title and description. To search
        names only see ``search_by_name``.

        :param query: The query string to filter subreddits by.

        """
        self._safely_add_arguments(generator_kwargs, 'params', q=query)
        return ListingGenerator(self._reddit, API_PATH['subreddits_search'],
                                **generator_kwargs)

    def search_by_name(self, query, include_nsfw=True, exact=False):
        """Return list of Subreddits whose names begin with ``query``.

        :param query: Search for subreddits beginning with this string.
        :param include_nsfw: Include subreddits labeled NSFW (default: True).
        :param exact: Return only exact matches to ``query`` (default: False).

        """
        result = self._reddit.post(API_PATH['subreddits_name_search'],
                                   data={'include_over_18': include_nsfw,
                                         'exact': exact, 'query': query})
        return [self._reddit.subreddit(x) for x in result['names']]

    def search_by_topic(self, query):
        """Return list of Subreddits whose topics match ``query``.

        :param query: Search for subreddits relevant to the search topic.

        """
        result = self._reddit.get(API_PATH['subreddits_by_topic'],
                                  params={'query': query})
        return [self._reddit.subreddit(x['name']) for x in result
                if x.get('name')]

    def stream(self):
        """Yield new subreddits as they are created.

        Subreddits are yielded oldest first. Up to 100 historical subreddits
        will initially be returned.

        """
        return stream_generator(self.new)
