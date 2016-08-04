"""Provide the RedditorListingMixin class."""
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from ..generator import ListingGenerator
from .base import BaseListingMixin
from .gilded import GildedListingMixin


class RedditorListingMixin(BaseListingMixin, GildedListingMixin):
    """Adds additional methods pertaining to Redditor instances."""

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
