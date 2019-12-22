from ....const import API_PATH as API_PATH
from ...base import PRAWBase as PRAWBase
from ..generator import ListingGenerator as ListingGenerator
from typing import Any

class SubmissionListingMixin(PRAWBase):
    def duplicates(self, **generator_kwargs: Any): ...
