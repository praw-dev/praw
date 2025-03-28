"""Provide the SubmissionListingMixin class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from praw.const import API_PATH
from praw.models.base import PRAWBase
from praw.models.listing.generator import ListingGenerator

if TYPE_CHECKING:
    from collections.abc import Iterator

    import praw.models


class SubmissionListingMixin(PRAWBase):
    """Adds additional methods pertaining to :class:`.Submission` instances."""

    def duplicates(self, **generator_kwargs: str | int | dict[str, str]) -> Iterator[praw.models.Submission]:
        """Return a :class:`.ListingGenerator` for the submission's duplicates.

        Additional keyword arguments are passed in the initialization of
        :class:`.ListingGenerator`.

        Example usage:

        .. code-block:: python

            submission = reddit.submission("5or86n")

            for duplicate in submission.duplicates():
                # process each duplicate
                ...

        .. seealso::

            :meth:`.upvote`

        """
        url = API_PATH["duplicates"].format(submission_id=self.id)
        return ListingGenerator(self._reddit, url, **generator_kwargs)
