"""Provide the ListingMixin class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from ..listinggenerator import ListingGenerator
from ..prawmodel import PRAWModel
from ...const import API_PATH


def _prepare(praw_object, params, target):
    """Fix for Redditor methods that use a query param rather than subpath."""
    if praw_object.__dict__.get('_listing_use_sort'):
        params['sort'] = target
        return praw_object._path
    return urljoin(praw_object._path, target)


class BaseListingMixin(PRAWModel):
    """Adds minimum set of methods that apply to all listing objects."""

    VALID_TIME_FILTERS = {'all', 'day', 'hour', 'month', 'week', 'year'}

    @staticmethod
    def validate_time_filter(time_filter):
        """Raise ValueError if time_filter is not valid."""
        if time_filter not in ListingMixin.VALID_TIME_FILTERS:
            raise ValueError('time_filter must be one of: {}'.format(', '.join(
                ListingMixin.VALID_TIME_FILTERS)))

    def controversial(self, time_filter='all', **generator_kwargs):
        """Return a ListingGenerator for controversial submissions.

        :param time_filter: Can be one of: all, day, hour, month, week, year.
            (Default: all)

        Raise ``ValueError`` if ``time_filter`` is invalid.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        self.validate_time_filter(time_filter)
        generator_kwargs.setdefault('params', {})['t'] = time_filter
        url = _prepare(self, generator_kwargs['params'], 'controversial')
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def hot(self, **generator_kwargs):
        """Return a ListingGenerator for hot items.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        url = _prepare(self, generator_kwargs.setdefault('params', {}), 'hot')
        return ListingGenerator(self._reddit, url, **generator_kwargs)

    def new(self, **generator_kwargs):
        """Return a ListingGenerator for new items.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        url = _prepare(self, generator_kwargs.setdefault('params', {}), 'new')
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
        generator_kwargs.setdefault('params', {})['t'] = time_filter
        url = _prepare(self, generator_kwargs['params'], 'top')
        return ListingGenerator(self._reddit, url, **generator_kwargs)


class ListingMixin(BaseListingMixin):
    """Adds additional methods that apply to most Listing objects."""

    def gilded(self, **generator_kwargs):
        """Return a ListingGenerator for gilded items.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'gilded'),
                                **generator_kwargs)


class SubListing(BaseListingMixin):
    """Helper class for generating SubListing objects."""

    def __init__(self, reddit, base_path, subpath):
        """Initialize a SubListing instance.

        :param reddit: An instance of :class:`.Reddit'.
        :param base_path: The path to the object up to this point.
        :param subpath: The additional path to this sublisting.

        """
        super(SubListing, self).__init__(reddit, None)
        self._listing_use_sort = True
        self._reddit = reddit
        self._path = urljoin(base_path, subpath)


class RedditorListingMixin(ListingMixin):
    """Adds additional methods pertaing to Redditor instances."""

    @property
    def comments(self):
        """An attribute representing the comments made by the Redditor."""
        if self.__dict__.get('_comments') is None:
            self._comments = SubListing(self._reddit, self._path, 'comments')
        return self._comments

    @property
    def submissions(self):
        """An attribute representing the submissions made by the Redditor."""
        if self.__dict__.get('_submissions') is None:
            self._submissions = SubListing(self._reddit, self._path,
                                           'submitted')
        return self._submissions

    def downvoted(self, **generator_kwargs):
        """Return a ListingGenerator for items the user has downvoted.

        May raise ``prawcore.Forbidden`` after issuing the request if the user
        is not authorized to access the list. Note that because this function
        returns a ``ListingGenerator`` the exception may not occur until
        sometime after this function has returned.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'downvoted'),
                                **generator_kwargs)

    def gildings(self, **generator_kwargs):
        """Return a ListingGenerator for items the user has gilded.

        May raise ``prawcore.Forbidden`` after issuing the request if the user
        is not authorized to access the list. Note that because this function
        returns a ``ListingGenerator`` the exception may not occur until
        sometime after this function has returned.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit,
                                urljoin(self._path, 'gilded/given'),
                                **generator_kwargs)

    def hidden(self, **generator_kwargs):
        """Return a ListingGenerator for items the user has hidden.

        May raise ``prawcore.Forbidden`` after issuing the request if the user
        is not authorized to access the list. Note that because this function
        returns a ``ListingGenerator`` the exception may not occur until
        sometime after this function has returned.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'hidden'),
                                **generator_kwargs)

    def saved(self, **generator_kwargs):
        """Return a ListingGenerator for items the user has saved.

        May raise ``prawcore.Forbidden`` after issuing the request if the user
        is not authorized to access the list. Note that because this function
        returns a ``ListingGenerator`` the exception may not occur until
        sometime after this function has returned.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'saved'),
                                **generator_kwargs)

    def upvoted(self, **generator_kwargs):
        """Return a ListingGenerator for items the user has upvoted.

        May raise ``prawcore.Forbidden`` after issuing the request if the user
        is not authorized to access the list. Note that because this function
        returns a ``ListingGenerator`` the exception may not occur until
        sometime after this function has returned.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'upvoted'),
                                **generator_kwargs)


class SubmissionListingMixin(ListingMixin):
    """Adds additional methods pertaining to Submission instances."""

    def duplicates(self, **generator_kwargs):
        """Return a ListingGenerator for the submission's duplicates.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        url = API_PATH['duplicates'].format(submission_id=self.id)
        return ListingGenerator(self._reddit, url, **generator_kwargs)


class SubredditListingMixin(ListingMixin):
    """Adds additional methods pertianing to Subreddit-like instances."""

    def rising(self, **generator_kwargs):
        """Return a ListingGenerator for rising submissions.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        return ListingGenerator(self._reddit, urljoin(self._path, 'rising'),
                                **generator_kwargs)
