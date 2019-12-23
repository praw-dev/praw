from typing import Generator

from ...base import PRAWBase as PRAWBase
from ...reddit.submission import Submission


class RisingListingMixin(PRAWBase):
    def random_rising(self, **generator_kwargs: str) -> Generator[Submission]: ...
    def rising(self, **generator_kwargs: str) -> Generator[Submission]: ...
