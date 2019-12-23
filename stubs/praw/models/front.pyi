from .listing.mixins import SubredditListingMixin as SubredditListingMixin
from ..reddit import Reddit


class Front(SubredditListingMixin):
    def __init__(self, reddit: Reddit) -> None: ...
    def best(self, **generator_kwargs: str): ...
