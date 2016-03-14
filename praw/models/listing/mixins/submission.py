"""Provide the SubmissionListingMixin class."""
from ....const import API_PATH
from ..generator import ListingGenerator
from .listing import ListingMixin


class SubmissionListingMixin(ListingMixin):
    """Adds additional methods pertaining to Submission instances."""

    def duplicates(self, **generator_kwargs):
        """Return a ListingGenerator for the submission's duplicates.

        Additional keyword arguments are passed to the ``ListingGenerator``
        constructor.

        """
        url = API_PATH['duplicates'].format(submission_id=self.id)
        return ListingGenerator(self._reddit, url, **generator_kwargs)
