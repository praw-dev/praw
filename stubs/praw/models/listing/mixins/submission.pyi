from ...base import PRAWBase as PRAWBase
from typing import Generator
from ...reddit.submission import Submission
from typing import Generator

from ...base import PRAWBase as PRAWBase
from ...reddit.submission import Submission


class SubmissionListingMixin(PRAWBase):
    def duplicates(self, **generator_kwargs: str) -> Generator[Submission]: ...
