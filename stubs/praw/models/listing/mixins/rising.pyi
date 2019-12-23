from ... import ListingGenerator
from ...base import PRAWBase as PRAWBase
from ...reddit.submission import Submission


class RisingListingMixin(PRAWBase):
    def random_rising(self, **generator_kwargs: str) -> ListingGenerator[Submission]: ...
    def rising(self, **generator_kwargs: str) -> ListingGenerator[Submission]: ...
