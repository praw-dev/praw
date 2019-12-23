from typing import Any, Generator

from ...base import PRAWBase as PRAWBase


class GildedListingMixin(PRAWBase):
    def gilded(self, **generator_kwargs: str) -> Generator[Any]: ...
