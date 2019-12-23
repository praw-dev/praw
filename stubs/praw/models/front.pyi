from .listing.mixins import SubredditListingMixin as SubredditListingMixin
from typing import Any
from typing import Any

from .listing.mixins import SubredditListingMixin as SubredditListingMixin


class Front(SubredditListingMixin):
    _path: str = ...
    def __init__(self, reddit: Any) -> None: ...
    def best(self, **generator_kwargs: Any): ...
