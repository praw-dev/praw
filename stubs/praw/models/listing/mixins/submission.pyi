from ... import ListingGenerator

from ...base import PRAWBase as PRAWBase
from ...reddit.submission import Submission


class SubmissionListingMixin(PRAWBase):
    def duplicates(self, **generator_kwargs: str) -> ListingGenerator[Submission]: ...
