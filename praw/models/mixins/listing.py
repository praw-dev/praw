from six.moves.urllib.parse import urljoin

from ..listinggenerator import ListingGenerator
from ..prawmodel import PRAWModel


class Listing(PRAWModel):
    """Adds methods that apply to listing objects."""

    VALID_TIME_FILTERS = {'all', 'day', 'hour', 'month', 'week', 'year'}

    @staticmethod
    def validate_time_filter(time_filter):
        if time_filter not in Listing.VALID_TIME_FILTERS:
            raise ValueError('time_filter must be one of: {}'.format(', '.join(
                Listing.VALID_TIME_FILTERS)))

    def controversial(self, time_filter='all', **generator_kwargs):
        """Return a ListingGenerator for controversial submissions.

        :param time_filter: Can be one of: all, day, hour, month, week, year.
            (Default: all)

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        self.validate_time_filter(time_filter)
        generator_kwargs.setdefault('params', {})['t'] = time_filter
        return ListingGenerator(self._reddit,
                                urljoin(self._url, 'controversial'),
                                **generator_kwargs)

    def gilded(self, **generator_kwargs):
        """Return a ListingGenerator for gilded submissions.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._url, 'gilded'),
                                **generator_kwargs)

    def hot(self, **generator_kwargs):
        """Return a ListingGenerator for hot submissions.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._url, 'hot'),
                                **generator_kwargs)

    def new(self, **generator_kwargs):
        """Return a ListingGenerator for new submissions.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._url, 'new'),
                                **generator_kwargs)

    def rising(self, **generator_kwargs):
        """Return a ListingGenerator for rising submissions.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._url, 'rising'),
                                **generator_kwargs)

    def top(self, time_filter='all', **generator_kwargs):
        """Return a ListingGenerator for top submissions.

        :param time_filter: Can be one of: all, day, hour, month, week, year.
            (Default: all)

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        self.validate_time_filter(time_filter)
        generator_kwargs.setdefault('params', {})['t'] = time_filter
        return ListingGenerator(self._reddit,
                                urljoin(self._url, 'controversial'),
                                **generator_kwargs)
