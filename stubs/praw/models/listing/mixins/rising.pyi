from ...base import PRAWBase as PRAWBase
from ..generator import ListingGenerator as ListingGenerator
from typing import Any

class RisingListingMixin(PRAWBase):
    def random_rising(self, **generator_kwargs: Any): ...
    def rising(self, **generator_kwargs: Any): ...
