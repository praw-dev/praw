from typing import Any

from ... import ListingGenerator
from ...base import PRAWBase as PRAWBase


class GildedListingMixin(PRAWBase):
    def gilded(self, **generator_kwargs: str) -> ListingGenerator[Any]: ...
