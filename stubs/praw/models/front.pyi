from .listing.generator import ListingGenerator as ListingGenerator
from .listing.mixins import SubredditListingMixin as SubredditListingMixin
from typing import Any

class Front(SubredditListingMixin):
    def __init__(self, reddit: Any) -> None: ...
    def best(self, **generator_kwargs: Any): ...
