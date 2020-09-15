"""Provide the SubmissionListingMixin class."""
from typing import TYPE_CHECKING, Dict, Iterator, Union

from ....const import API_PATH
from ...base import PRAWBase
from ..generator import ListingGenerator

if TYPE_CHECKING:  # pragma: no cover
    from ...reddit.submission import Submission  # noqa: F401


class SubmissionListingMixin(PRAWBase):
    """Adds additional methods pertaining to Submission instances."""

    def duplicates(
        self, **generator_kwargs: Union[str, int, Dict[str, str]]
    ) -> Iterator["Submission"]:
        """Return a :class:`.ListingGenerator` for the submission's duplicates.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        Example usage:

        .. code-block:: python

            submission = reddit.submission(id="5or86n")

            for duplicate in submission.duplicates():
                # process each duplicate
                ...

        .. seealso::

            :meth:`~.upvote`

        """
        url = API_PATH["duplicates"].format(submission_id=self.id)
        return ListingGenerator(self._reddit, url, **generator_kwargs)
