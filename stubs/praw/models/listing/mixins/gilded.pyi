from ...base import PRAWBase as PRAWBase
from ..generator import ListingGenerator as ListingGenerator
from typing import Any

class GildedListingMixin(PRAWBase):
    def gilded(self, **generator_kwargs: Any): ...
