"""Provide the BaseListingMixin class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from ...base import PRAWBase
from ..generator import ListingGenerator


def _prepare(praw_object, arguments_dict, target):
    """Fix for Redditor methods that use a query param rather than subpath."""
    if praw_object.__dict__.get('_listing_use_sort'):
        PRAWBase._safely_add_arguments(arguments_dict, 'params', sort=target)
        return praw_object._path
    return urljoin(praw_object._path, target)


class BaseListingMixin(PRAWBase):
    """Adds minimum set of methods that apply to all listing objects."""

    VALID_TIME_FILTERS = {'all', 'day', 'hour', 'month', 'week', 'year'}

    @staticmethod
    def validate_time_filter(time_filter):
        """Raise ValueError if time_filter is not valid."""
        if time_filter not in BaseListingMixin.VALID_TIME_FILTERS:
            raise ValueError('time_filter must be one of: {}'.format(', '.join(
                BaseListingMixin.VALID_TIME_FILTERS)))

    def controversial(self, time_filter='all', **generator_kwargs):
        """Return a ListingGenerator for controversial submissions.

        :param time_filter: Can be one of: all, day, hour, month, week, year.
            (Default: all)

        Raise ``ValueError`` if ``time_filter`` is invalid.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        self.validate_time_filter(time_filter)
        self._safely_add_arguments(generator_kwargs, 'params', t=time_filter)
        url = _prepare(self, generator_kwargs, 'controversial')
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def hot(self, **generator_kwargs):
        """Return a ListingGenerator for hot items.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        generator_kwargs.setdefault('params', {})
        url = _prepare(self, generator_kwargs, 'hot')
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def new(self, **generator_kwargs):
        """Return a ListingGenerator for new items.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        generator_kwargs.setdefault('params', {})
        url = _prepare(self, generator_kwargs, 'new')
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def top(self, time_filter='all', **generator_kwargs):
        """Return a ListingGenerator for top submissions.

        :param time_filter: Can be one of: all, day, hour, month, week, year.
            (Default: all)

        Raise ``ValueError`` if ``time_filter`` is invalid.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        self.validate_time_filter(time_filter)
        self._safely_add_arguments(generator_kwargs, 'params', t=time_filter)
        url = _prepare(self, generator_kwargs, 'top')
        return ListingGenerator(self._reddit, url, **generator_kwargs)
