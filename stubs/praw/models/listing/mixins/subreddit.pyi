from ...base import PRAWBase as PRAWBase
from .base import BaseListingMixin as BaseListingMixin
from .gilded import GildedListingMixin as GildedListingMixin
from .rising import RisingListingMixin as RisingListingMixin
from typing import Any
from typing import Any

from .base import BaseListingMixin as BaseListingMixin
from .gilded import GildedListingMixin as GildedListingMixin
from .rising import RisingListingMixin as RisingListingMixin
from ...base import PRAWBase as PRAWBase


class SubredditListingMixin(BaseListingMixin, GildedListingMixin, RisingListingMixin):
    def comments(self): ...
    def __init__(self, reddit: Any, _data: Any) -> None: ...

class CommentHelper(PRAWBase):
    @property
    def _path(self): ...
    subreddit: Any = ...
    def __init__(self, subreddit: Any) -> None: ...
    def __call__(self, **generator_kwargs: Any): ...
